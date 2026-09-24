#!/usr/bin/env python3
"""Resolve Maven dependencies to real, readable source code.

Given a dependency coordinate (or an artifact/class name to look up against a
project's pom.xml chain), locates the artifact under ~/.m2/repository, and
either extracts its -sources.jar or decompiles the needed class with CFR into
a persistent cache. When no sources jar is present locally, `get` first tries
`mvn dependency:resolve-sources`/`resolve -Dclassifier=javadoc` to fetch one
before falling back to decompiling. Every subcommand prints one JSON object
to stdout and exits 0 on success, 1 on error (error JSON has an "error" key).

No third-party dependencies. Requires: python3, and for the decompile
fallback only, `java` on PATH (already required to build the project) plus
network access the first time a CFR-lacking dependency needs decompiling.
`mvn` on PATH is optional but lets `get` auto-download a missing sources jar
before decompiling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
import zipfile
from pathlib import Path
from typing import Any, NoReturn
from urllib.request import urlretrieve

CACHE_ROOT = Path.home() / ".cache" / "mvn-source-explorer"
M2_REPO = Path.home() / ".m2" / "repository"

CFR_VERSION = "0.152"
CFR_URL = f"https://repo1.maven.org/maven2/org/benf/cfr/{CFR_VERSION}/cfr-{CFR_VERSION}.jar"
CFR_SHA256 = "f686e8f3ded377d7bc87d216a90e9e9512df4156e75b06c655a16648ae8765b2"
CFR_JAR_PATH = CACHE_ROOT / "tools" / f"cfr-{CFR_VERSION}.jar"

PROPERTY_PATTERN = re.compile(r"\$\{([\w.\-]+)\}")


def emit(payload: dict[str, Any], isError: bool = False) -> NoReturn:
    print(json.dumps(payload, indent=2))
    sys.exit(1 if isError else 0)


# ---------------------------------------------------------------------------
# pom.xml chain parsing (best-effort: plain properties + dependencyManagement
# visible in the module + parent chain. BOM <import>s and profile-activated
# properties are NOT resolved here -- unresolved versions fall back to `mvn`.)
# ---------------------------------------------------------------------------


def stripNamespace(tag: str) -> str:
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def findPomChain(startDir: Path) -> list[Path]:
    current = startDir.resolve()
    leafPom = None
    for candidate in [current, *current.parents]:
        if (candidate / "pom.xml").is_file():
            leafPom = candidate / "pom.xml"
            break
    if leafPom is None:
        return []

    chain: list[Path] = []
    visited: set[Path] = set()
    pomPath = leafPom
    for _ in range(10):
        if pomPath in visited or not pomPath.is_file():
            break
        visited.add(pomPath)
        chain.append(pomPath)
        parentRelativePath = readParentRelativePath(pomPath)
        if parentRelativePath is None:
            break
        pomPath = (pomPath.parent / parentRelativePath).resolve()
    return chain


def readParentRelativePath(pomPath: Path) -> str | None:
    root = ElementTree.parse(pomPath).getroot()  # nosec B314 - local pom.xml already trusted to build the project; not untrusted/network XML
    for child in root:
        if stripNamespace(child.tag) != "parent":
            continue
        relativePath = "../pom.xml"
        for grandchild in child:
            if stripNamespace(grandchild.tag) == "relativePath":
                relativePath = (grandchild.text or "").strip() or "../pom.xml"
        return relativePath
    return None


def parsePom(pomPath: Path) -> dict[str, Any]:
    root = ElementTree.parse(pomPath).getroot()  # nosec B314 - local pom.xml already trusted to build the project; not untrusted/network XML

    def findChild(element: ElementTree.Element, name: str) -> ElementTree.Element | None:
        for child in element:
            if stripNamespace(child.tag) == name:
                return child
        return None

    def findChildren(element: ElementTree.Element, name: str) -> list[ElementTree.Element]:
        return [child for child in element if stripNamespace(child.tag) == name]

    properties: dict[str, str] = {}
    propertiesElement = findChild(root, "properties")
    if propertiesElement is not None:
        for propertyElement in propertiesElement:
            properties[stripNamespace(propertyElement.tag)] = (propertyElement.text or "").strip()

    dependencyManagement: dict[str, dict[str, Any]] = {}
    dependencyManagementElement = findChild(root, "dependencyManagement")
    if dependencyManagementElement is not None:
        dependenciesElement = findChild(dependencyManagementElement, "dependencies")
        if dependenciesElement is not None:
            for dependencyElement in findChildren(dependenciesElement, "dependency"):
                managedGroupIdElement = findChild(dependencyElement, "groupId")
                managedArtifactIdElement = findChild(dependencyElement, "artifactId")
                managedVersionElement = findChild(dependencyElement, "version")
                if (
                    managedGroupIdElement is not None
                    and managedArtifactIdElement is not None
                    and managedVersionElement is not None
                ):
                    managedGroupId = (managedGroupIdElement.text or "").strip()
                    managedArtifactId = (managedArtifactIdElement.text or "").strip()
                    dependencyManagement[f"{managedGroupId}:{managedArtifactId}"] = {
                        "version": (managedVersionElement.text or "").strip(),
                        "managedIn": str(pomPath),
                        "managedAtLine": findDeclaredLine(
                            pomPath, managedGroupId, managedArtifactId
                        ),
                    }

    dependencies: list[dict[str, Any]] = []
    dependenciesElement = findChild(root, "dependencies")
    if dependenciesElement is not None:
        for dependencyElement in findChildren(dependenciesElement, "dependency"):
            groupIdElement = findChild(dependencyElement, "groupId")
            artifactIdElement = findChild(dependencyElement, "artifactId")
            versionElement = findChild(dependencyElement, "version")
            if groupIdElement is None or artifactIdElement is None:
                continue
            groupId = (groupIdElement.text or "").strip()
            artifactId = (artifactIdElement.text or "").strip()
            dependencies.append(
                {
                    "groupId": groupId,
                    "artifactId": artifactId,
                    "rawVersion": (versionElement.text or "").strip()
                    if versionElement is not None and versionElement.text
                    else None,
                    "declaredIn": str(pomPath),
                    "declaredAtLine": findDeclaredLine(pomPath, groupId, artifactId),
                }
            )

    return {
        "properties": properties,
        "dependencyManagement": dependencyManagement,
        "dependencies": dependencies,
    }


def findDeclaredLine(pomPath: Path, groupId: str, artifactId: str) -> int | None:
    text = pomPath.read_text(encoding="utf-8", errors="replace")
    groupPattern = re.compile(rf"<groupId>\s*{re.escape(groupId)}\s*</groupId>")
    artifactPattern = re.compile(rf"<artifactId>\s*{re.escape(artifactId)}\s*</artifactId>")
    for blockMatch in re.finditer(r"<dependency>.*?</dependency>", text, re.DOTALL):
        block = blockMatch.group(0)
        if groupPattern.search(block) and artifactPattern.search(block):
            return 1 + text.count("\n", 0, blockMatch.start())
    return None


def substituteProperties(
    rawValue: str | None, properties: dict[str, str]
) -> tuple[str | None, bool]:
    if rawValue is None:
        return None, False
    value = rawValue
    for _ in range(5):
        match = PROPERTY_PATTERN.search(value)
        if match is None:
            return value, True
        replacement = properties.get(match.group(1))
        if replacement is None:
            return value, False
        value = value[: match.start()] + replacement + value[match.end() :]
    return value, False


def mavenFallbackVersions(leafProjectDir: Path) -> dict[str, str]:
    if shutil.which("mvn") is None:
        return {}

    with tempfile.TemporaryDirectory() as tempDir:
        outputFile = Path(tempDir) / "dependency-list.txt"
        try:
            subprocess.run(
                [
                    "mvn",
                    "-q",
                    "-B",
                    "dependency:list",
                    "-Dsort=false",
                    f"-DoutputFile={outputFile}",
                ],
                cwd=leafProjectDir,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError):
            return {}
        if not outputFile.is_file():
            return {}
        lines = outputFile.read_text(encoding="utf-8", errors="replace").splitlines()

    versions: dict[str, str] = {}
    for rawLine in lines:
        line = rawLine.strip().split(" -- ", 1)[0]
        # groupId:artifactId:packaging[:classifier]:version:scope
        fields = line.split(":")
        if len(fields) < 5:
            continue
        groupId, artifactId, version = fields[0], fields[1], fields[-2]
        if (
            re.fullmatch(r"[\w.\-]+", groupId)
            and re.fullmatch(r"[\w.\-]+", artifactId)
            and re.fullmatch(r"[\w.\-]+", version)
        ):
            versions[f"{groupId}:{artifactId}"] = version
    return versions


def listDependencies(projectDir: str) -> list[dict[str, Any]] | None:
    chain = findPomChain(Path(projectDir))
    if not chain:
        return None

    parsedPoms = [parsePom(pomPath) for pomPath in chain]
    # Chain is leaf-first; merge root-to-leaf so a child overrides its parent.
    properties: dict[str, str] = {}
    dependencyManagement: dict[str, dict[str, Any]] = {}
    for parsed in reversed(parsedPoms):
        properties.update(parsed["properties"])
        dependencyManagement.update(parsed["dependencyManagement"])
    for managementEntry in dependencyManagement.values():
        resolvedVersion, _isFullyResolved = substituteProperties(
            managementEntry["version"], properties
        )
        managementEntry["version"] = resolvedVersion

    dependencies: dict[str, dict[str, Any]] = {}
    for parsed in reversed(parsedPoms):
        for dependency in parsed["dependencies"]:
            key = f"{dependency['groupId']}:{dependency['artifactId']}"
            dependencies[key] = dependency  # leaf-most declaration wins

    resolvedDependencies: list[dict[str, Any]] = []
    unresolvedKeys: list[str] = []
    for key, dependency in dependencies.items():
        matchedManagementEntry = dependencyManagement.get(key)
        rawVersion = dependency["rawVersion"] or (
            matchedManagementEntry["version"] if matchedManagementEntry else None
        )
        version, isFullyResolved = substituteProperties(rawVersion, properties)
        entry = {**dependency, "version": version}
        if dependency["rawVersion"] is None and matchedManagementEntry is not None:
            entry["versionManagedIn"] = matchedManagementEntry["managedIn"]
            entry["versionManagedAtLine"] = matchedManagementEntry["managedAtLine"]
        resolvedDependencies.append(entry)
        if not isFullyResolved:
            unresolvedKeys.append(key)

    if unresolvedKeys:
        fallbackVersions = mavenFallbackVersions(chain[0].parent)
        for entry in resolvedDependencies:
            key = f"{entry['groupId']}:{entry['artifactId']}"
            if key in unresolvedKeys and key in fallbackVersions:
                entry["version"] = fallbackVersions[key]
                entry["versionSource"] = "mvn dependency:list (property/BOM fallback)"

    return resolvedDependencies


def localRepoPaths(groupId: str, artifactId: str, version: str) -> tuple[Path, Path]:
    groupPath = groupId.replace(".", "/")
    base = M2_REPO / groupPath / artifactId / version
    jarPath = base / f"{artifactId}-{version}.jar"
    sourcesJarPath = base / f"{artifactId}-{version}-sources.jar"
    return jarPath, sourcesJarPath


def resolveCoordinate(coordinate: str, projectDir: str) -> dict[str, Any]:
    parts = coordinate.split(":")
    if len(parts) == 3:
        groupId, artifactId, version = parts
        declaredIn = None
        declaredAtLine = None
        versionManagedIn = None
        versionManagedAtLine = None
    else:
        dependencies = listDependencies(projectDir)
        if dependencies is None:
            return {"error": f"No pom.xml found at or above {projectDir}"}
        if len(parts) == 2:
            queryGroupId, artifactId = parts
            matches = [
                d
                for d in dependencies
                if d["groupId"] == queryGroupId and d["artifactId"] == artifactId
            ]
        else:
            artifactId = parts[0]
            matches = [d for d in dependencies if d["artifactId"] == artifactId]
        if not matches:
            return {
                "error": f"'{coordinate}' not found among dependencies declared in the pom.xml chain under {projectDir}. Run the 'list' subcommand to see what's declared."
            }
        if len(matches) > 1:
            return {
                "error": f"'{coordinate}' is ambiguous, found in multiple groups: {[d['groupId'] for d in matches]}. Qualify with group:artifact."
            }
        match = matches[0]
        groupId, artifactId, version = match["groupId"], match["artifactId"], match["version"]
        declaredIn, declaredAtLine = match["declaredIn"], match["declaredAtLine"]
        versionManagedIn = match.get("versionManagedIn")
        versionManagedAtLine = match.get("versionManagedAtLine")
        if version is None or PROPERTY_PATTERN.search(version):
            return {
                "error": f"Could not resolve a version for {groupId}:{artifactId} from the pom.xml chain or `mvn dependency:list`."
            }

    jarPath, sourcesJarPath = localRepoPaths(groupId, artifactId, version)
    return {
        "groupId": groupId,
        "artifactId": artifactId,
        "version": version,
        "declaredIn": declaredIn,
        "declaredAtLine": declaredAtLine,
        "versionManagedIn": versionManagedIn,
        "versionManagedAtLine": versionManagedAtLine,
        "jarPath": str(jarPath),
        "sourcesJarPath": str(sourcesJarPath),
        "hasJar": jarPath.is_file(),
        "hasSources": sourcesJarPath.is_file(),
    }


# ---------------------------------------------------------------------------
# Sources-jar download fallback (tried before CFR; only when hasSources is false)
# ---------------------------------------------------------------------------


def attemptSourcesDownload(groupId: str, artifactId: str, version: str, projectDir: str) -> bool:
    if shutil.which("mvn") is None:
        return False
    gav = f"{groupId}:{artifactId}:{version}"
    print(
        f"[mvn-source-explorer] no local sources jar for {gav}; running `mvn dependency:resolve-sources`",
        file=sys.stderr,
    )
    try:
        subprocess.run(
            [
                "mvn",
                "-q",
                "-B",
                "dependency:resolve-sources",
                f"-DincludeArtifact={gav}",
                "dependency:resolve",
                "-Dclassifier=javadoc",
                f"-DincludeArtifacts={gav}",
            ],
            cwd=projectDir,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return False
    _, sourcesJarPath = localRepoPaths(groupId, artifactId, version)
    return sourcesJarPath.is_file()


# ---------------------------------------------------------------------------
# CFR decompile fallback (only used when hasSources is false and the sources
# download above didn't produce a sources jar)
# ---------------------------------------------------------------------------


def sha256Of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fileHandle:
        for chunk in iter(lambda: fileHandle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensureCfrJar() -> Path:
    if CFR_JAR_PATH.is_file() and sha256Of(CFR_JAR_PATH) == CFR_SHA256:
        return CFR_JAR_PATH
    CFR_JAR_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(
        f"[mvn-source-explorer] downloading CFR decompiler (one-time, ~2MB) from {CFR_URL}",
        file=sys.stderr,
    )
    tempPath = CFR_JAR_PATH.with_suffix(".jar.download")
    urlretrieve(CFR_URL, tempPath)  # nosec B310 - fixed https URL to a pinned artifact; result is sha256-verified before use
    if sha256Of(tempPath) != CFR_SHA256:
        tempPath.unlink(missing_ok=True)
        raise RuntimeError(
            f"Downloaded CFR jar failed checksum verification against pinned sha256 {CFR_SHA256}"
        )
    tempPath.replace(CFR_JAR_PATH)
    return CFR_JAR_PATH


def decompileClass(jarPath: Path, fullyQualifiedClassName: str, outputDir: Path) -> dict[str, Any]:
    if shutil.which("java") is None:
        return {"error": "`java` is not on PATH; required to run the CFR decompiler."}
    cfrJarPath = ensureCfrJar()
    outputDir.mkdir(parents=True, exist_ok=True)
    classFilter = "^" + re.escape(fullyQualifiedClassName) + r"(\$.*)?$"
    result = subprocess.run(
        [
            "java",
            "-jar",
            str(cfrJarPath),
            str(jarPath),
            "--jarfilter",
            classFilter,
            "--outputdir",
            str(outputDir),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    classFilePath = outputDir / (fullyQualifiedClassName.replace(".", "/") + ".java")
    if not classFilePath.is_file():
        return {
            "error": f"CFR did not produce {classFilePath}. stdout: {result.stdout[-2000:]} stderr: {result.stderr[-2000:]}"
        }
    return {"classFile": str(classFilePath)}


# ---------------------------------------------------------------------------
# subcommands
# ---------------------------------------------------------------------------


def commandList(args: argparse.Namespace) -> None:
    dependencies = listDependencies(args.project_dir)
    if dependencies is None:
        emit({"error": f"No pom.xml found at or above {args.project_dir}"}, isError=True)
    emit({"dependencies": dependencies})


def commandResolve(args: argparse.Namespace) -> None:
    result = resolveCoordinate(args.coordinate, args.project_dir)
    emit(result, isError="error" in result)


def commandGet(args: argparse.Namespace) -> None:
    resolved = resolveCoordinate(args.coordinate, args.project_dir)
    if "error" in resolved:
        emit(resolved, isError=True)

    if not resolved["hasSources"] and attemptSourcesDownload(
        resolved["groupId"], resolved["artifactId"], resolved["version"], args.project_dir
    ):
        resolved["hasSources"] = True

    groupPath = resolved["groupId"].replace(".", "/")
    cacheBase = CACHE_ROOT / groupPath / resolved["artifactId"] / resolved["version"]

    if resolved["hasSources"]:
        sourcesCacheDir = cacheBase / "sources"
        alreadyExtracted = sourcesCacheDir.is_dir() and any(sourcesCacheDir.iterdir())
        if not alreadyExtracted:
            sourcesCacheDir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(resolved["sourcesJarPath"]) as sourcesJar:
                sourcesJar.extractall(sourcesCacheDir)
        result = {**resolved, "mode": "sources", "cacheDir": str(sourcesCacheDir)}
        if args.fqcn:
            outerClassName = args.fqcn.split("$", 1)[0]
            classFilePath = sourcesCacheDir / (outerClassName.replace(".", "/") + ".java")
            result["classFile"] = str(classFilePath) if classFilePath.is_file() else None
        emit(result)

    if not resolved["hasJar"]:
        emit(
            {
                **resolved,
                "error": "Neither the jar nor a sources jar is present locally. Run a build (e.g. `mvn dependency:resolve`) first.",
            },
            isError=True,
        )

    if not args.fqcn:
        emit(
            {
                **resolved,
                "error": "No sources jar available for this artifact. Pass --class <FullyQualifiedClassName> to decompile a specific class with CFR.",
            },
            isError=True,
        )

    decompiledCacheDir = cacheBase / "decompiled"
    decompileResult = decompileClass(Path(resolved["jarPath"]), args.fqcn, decompiledCacheDir)
    if "error" in decompileResult:
        emit({**resolved, **decompileResult}, isError=True)
    emit(
        {
            **resolved,
            "mode": "decompiled",
            "cacheDir": str(decompiledCacheDir),
            "classFile": decompileResult["classFile"],
            "note": "Decompiled from bytecode with CFR -- logic and control flow are accurate; types from classes outside this jar may show as raw/erased signatures.",
        }
    )


def commandFindClass(args: argparse.Namespace) -> None:
    dependencies = listDependencies(args.project_dir)
    if dependencies is None:
        emit({"error": f"No pom.xml found at or above {args.project_dir}"}, isError=True)

    isFullyQualified = "." in args.name
    javaSuffix = args.name.replace(".", "/") + ".java" if isFullyQualified else f"/{args.name}.java"
    classSuffix = (
        args.name.replace(".", "/") + ".class" if isFullyQualified else f"/{args.name}.class"
    )

    matches: list[dict[str, Any]] = []
    searched: list[str] = []
    for dependency in dependencies:
        if not dependency.get("version"):
            continue
        jarPath, sourcesJarPath = localRepoPaths(
            dependency["groupId"], dependency["artifactId"], dependency["version"]
        )
        gav = f"{dependency['groupId']}:{dependency['artifactId']}:{dependency['version']}"
        if sourcesJarPath.is_file():
            searched.append(gav)
            with zipfile.ZipFile(sourcesJarPath) as sourcesJar:
                matches.extend(
                    {"gav": gav, "entry": entryName, "hasSources": True}
                    for entryName in sourcesJar.namelist()
                    if entryName == javaSuffix.lstrip("/") or entryName.endswith(javaSuffix)
                )
        elif jarPath.is_file():
            searched.append(gav)
            with zipfile.ZipFile(jarPath) as jar:
                matches.extend(
                    {"gav": gav, "entry": entryName, "hasSources": False}
                    for entryName in jar.namelist()
                    if entryName == classSuffix.lstrip("/") or entryName.endswith(classSuffix)
                )

    emit({"matches": matches, "searchedDependencies": searched})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    listParser = subparsers.add_parser(
        "list", help="List dependencies declared in the pom.xml chain for a project"
    )
    listParser.add_argument("--project-dir", default=".", help="Project directory (default: cwd)")
    listParser.set_defaults(handler=commandList)

    resolveParser = subparsers.add_parser(
        "resolve", help="Resolve a coordinate to its local jar/sources-jar paths"
    )
    resolveParser.add_argument(
        "coordinate", help="group:artifact:version, group:artifact, or artifact"
    )
    resolveParser.add_argument("--project-dir", default=".")
    resolveParser.set_defaults(handler=commandResolve)

    getParser = subparsers.add_parser(
        "get",
        help="Ensure source is available locally (extract sources jar or CFR-decompile a class); print the path",
    )
    getParser.add_argument("coordinate", help="group:artifact:version, group:artifact, or artifact")
    getParser.add_argument("--project-dir", default=".")
    getParser.add_argument(
        "--class",
        dest="fqcn",
        default=None,
        help="Fully qualified class name; required when no sources jar exists",
    )
    getParser.set_defaults(handler=commandGet)

    findClassParser = subparsers.add_parser(
        "find-class", help="Find which declared dependency contains a given class"
    )
    findClassParser.add_argument("name", help="Simple class name or fully qualified class name")
    findClassParser.add_argument("--project-dir", default=".")
    findClassParser.set_defaults(handler=commandFindClass)

    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
