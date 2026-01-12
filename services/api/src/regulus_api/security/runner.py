from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FindingRecord:
    tool: str
    severity: str
    file_path: str | None
    line: int | None
    message: str
    rule_id: str | None
    metadata: dict | None


@dataclass
class ScanResult:
    tool: str
    findings: list[FindingRecord]
    summary: dict


def run_semgrep(repo_path: Path) -> ScanResult:
    result = run_command(
        ["semgrep", "--config=auto", "--json"],
        repo_path,
        allow_exit_codes={0, 1},
    )
    data = json.loads(result)
    findings: list[FindingRecord] = []
    for item in data.get("results", []):
        extra = item.get("extra", {})
        findings.append(
            FindingRecord(
                tool="semgrep",
                severity=str(extra.get("severity", "medium")),
                file_path=item.get("path"),
                line=item.get("start", {}).get("line"),
                message=str(extra.get("message", "")),
                rule_id=item.get("check_id"),
                metadata=item,
            )
        )
    summary = {
        "total": len(findings),
        "by_severity": tally([finding.severity for finding in findings]),
    }
    return ScanResult(tool="semgrep", findings=findings, summary=summary)


def run_pip_audit(repo_path: Path) -> ScanResult:
    result = run_command(
        ["pip-audit", "--format", "json"],
        repo_path,
        allow_exit_codes={0, 1},
    )
    data = json.loads(result or "[]")
    findings: list[FindingRecord] = []
    for entry in data if isinstance(data, list) else data.get("vulnerabilities", []):
        findings.append(
            FindingRecord(
                tool="pip-audit",
                severity=str(entry.get("severity", "medium")),
                file_path=None,
                line=None,
                message=str(entry.get("description", entry.get("id", "pip-audit finding"))),
                rule_id=entry.get("id"),
                metadata=entry,
            )
        )
    summary = {
        "total": len(findings),
        "by_severity": tally([finding.severity for finding in findings]),
    }
    return ScanResult(tool="pip-audit", findings=findings, summary=summary)


def run_npm_audit(repo_path: Path) -> ScanResult:
    result = run_command(
        ["npm", "audit", "--json"],
        repo_path,
        allow_exit_codes={0, 1},
    )
    data = json.loads(result or "{}")
    vulnerabilities = data.get("vulnerabilities", {})
    findings: list[FindingRecord] = []
    for name, vuln in vulnerabilities.items():
        findings.append(
            FindingRecord(
                tool="npm-audit",
                severity=str(vuln.get("severity", "medium")),
                file_path=None,
                line=None,
                message=str(vuln.get("title", name)),
                rule_id=name,
                metadata=vuln,
            )
        )
    summary = {
        "total": len(findings),
        "by_severity": tally([finding.severity for finding in findings]),
    }
    return ScanResult(tool="npm-audit", findings=findings, summary=summary)


def run_command(
    command: list[str],
    repo_path: Path,
    allow_exit_codes: set[int],
    timeout: int = 300,
) -> str:
    result = subprocess.run(
        command,
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode not in allow_exit_codes:
        raise RuntimeError(result.stderr.strip() or "security scan failed")
    return result.stdout


def tally(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
