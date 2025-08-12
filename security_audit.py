#!/usr/bin/env python3
"""
Security Audit Script for Artha AI
==================================

This script performs a comprehensive security audit of the Artha AI codebase
to identify potential vulnerabilities and security issues.
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import subprocess

class SecurityAuditor:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
        self.warnings = []
        self.info = []
        
    def log_issue(self, severity: str, category: str, file_path: str, line_number: int, description: str, recommendation: str = ""):
        """Log a security issue"""
        issue = {
            "severity": severity,
            "category": category,
            "file": str(file_path),
            "line": line_number,
            "description": description,
            "recommendation": recommendation
        }
        
        if severity == "HIGH":
            self.issues.append(issue)
        elif severity == "MEDIUM":
            self.warnings.append(issue)
        else:
            self.info.append(issue)
    
    def scan_hardcoded_secrets(self):
        """Scan for hardcoded secrets and credentials"""
        print("🔍 Scanning for hardcoded secrets...")
        
        # Patterns for different types of secrets
        patterns = {
            "password": r'(?i)(password|pwd)\s*[=:]\s*["\']([^"\']{8,})["\']',
            "api_key": r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([^"\']{20,})["\']',
            "secret": r'(?i)(secret|token)\s*[=:]\s*["\']([^"\']{16,})["\']',
            "private_key": r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
            "jwt_secret": r'(?i)jwt[_-]?secret\s*[=:]\s*["\']([^"\']{16,})["\']',
            "database_url": r'(?i)(database[_-]?url|db[_-]?url)\s*[=:]\s*["\']([^"\']*://[^"\']*:[^"\']*@[^"\']*)["\']'
        }
        
        exclude_patterns = [
            r'your[-_]',
            r'CHANGE[-_]',
            r'GENERATE[-_]',
            r'example',
            r'template',
            r'placeholder',
            r'<[^>]*>',
            r'\{[^}]*\}',
            r'\$[A-Z_]+',
            r'\.env\.example',
            r'SECURITY\.md',
            r'DEPLOYMENT\.md',
            r'README\.md'
        ]
        
        for file_path in self.get_source_files():
            if any(pattern in str(file_path) for pattern in ['.env.example', 'SECURITY.md', 'DEPLOYMENT.md']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern_name, pattern in patterns.items():
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            # Check if it's an excluded pattern
                            if any(re.search(exclude, line, re.IGNORECASE) for exclude in exclude_patterns):
                                continue
                                
                            self.log_issue(
                                "HIGH",
                                "Hardcoded Secrets",
                                file_path,
                                line_num,
                                f"Potential hardcoded {pattern_name}: {match.group(0)[:50]}...",
                                f"Move {pattern_name} to environment variables"
                            )
            except Exception as e:
                continue
    
    def scan_sql_injection(self):
        """Scan for potential SQL injection vulnerabilities"""
        print("🔍 Scanning for SQL injection vulnerabilities...")
        
        patterns = [
            r'execute\s*\(\s*["\'].*%s.*["\']',
            r'query\s*\(\s*["\'].*%s.*["\']',
            r'cursor\.execute\s*\(\s*["\'].*\+.*["\']',
            r'SELECT\s+.*\+.*FROM',
            r'INSERT\s+.*\+.*VALUES',
            r'UPDATE\s+.*\+.*SET',
            r'DELETE\s+.*\+.*WHERE'
        ]
        
        for file_path in self.get_source_files(['.py']):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.log_issue(
                                "HIGH",
                                "SQL Injection",
                                file_path,
                                line_num,
                                f"Potential SQL injection vulnerability: {line.strip()[:100]}...",
                                "Use parameterized queries or ORM methods"
                            )
            except Exception as e:
                continue
    
    def scan_xss_vulnerabilities(self):
        """Scan for potential XSS vulnerabilities"""
        print("🔍 Scanning for XSS vulnerabilities...")
        
        patterns = [
            r'innerHTML\s*=\s*.*\+',
            r'document\.write\s*\(',
            r'eval\s*\(',
            r'dangerouslySetInnerHTML',
            r'v-html\s*=',
            r'[^a-zA-Z]html\s*\+=',
        ]
        
        for file_path in self.get_source_files(['.js', '.jsx', '.ts', '.tsx', '.py']):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.log_issue(
                                "MEDIUM",
                                "XSS Vulnerability",
                                file_path,
                                line_num,
                                f"Potential XSS vulnerability: {line.strip()[:100]}...",
                                "Sanitize user input and use safe rendering methods"
                            )
            except Exception as e:
                continue
    
    def scan_insecure_dependencies(self):
        """Scan for known vulnerable dependencies"""
        print("🔍 Scanning for insecure dependencies...")
        
        # Check Python dependencies
        requirements_files = list(self.project_root.glob('**/requirements*.txt'))
        for req_file in requirements_files:
            try:
                with open(req_file, 'r') as f:
                    content = f.read()
                    
                # Check for unpinned versions
                unpinned = re.findall(r'^([a-zA-Z0-9_-]+)(?:\s*$|\s*>=)', content, re.MULTILINE)
                for package in unpinned:
                    self.log_issue(
                        "MEDIUM",
                        "Dependency Security",
                        req_file,
                        0,
                        f"Unpinned dependency version: {package}",
                        "Pin dependency versions to specific releases"
                    )
            except Exception as e:
                continue
        
        # Check Node.js dependencies
        package_files = list(self.project_root.glob('**/package.json'))
        for pkg_file in package_files:
            try:
                with open(pkg_file, 'r') as f:
                    data = json.load(f)
                    
                dependencies = data.get('dependencies', {})
                dev_dependencies = data.get('devDependencies', {})
                
                for dep, version in {**dependencies, **dev_dependencies}.items():
                    if version.startswith('^') or version.startswith('~') or version == '*':
                        self.log_issue(
                            "MEDIUM",
                            "Dependency Security",
                            pkg_file,
                            0,
                            f"Loose dependency version: {dep}@{version}",
                            "Use exact versions for better security"
                        )
            except Exception as e:
                continue
    
    def scan_file_permissions(self):
        """Scan for insecure file permissions"""
        print("🔍 Scanning file permissions...")
        
        sensitive_files = ['.env', 'config.py', 'settings.py', 'secrets.json']
        
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                filename = file_path.name.lower()
                
                if any(sensitive in filename for sensitive in sensitive_files):
                    try:
                        # Check if file is readable by others (Unix-like systems)
                        if hasattr(os, 'stat'):
                            stat_info = os.stat(file_path)
                            mode = stat_info.st_mode
                            
                            # Check if file is readable by group or others
                            if mode & 0o044:  # Group or others can read
                                self.log_issue(
                                    "MEDIUM",
                                    "File Permissions",
                                    file_path,
                                    0,
                                    f"Sensitive file has loose permissions: {oct(mode)[-3:]}",
                                    "Restrict file permissions to owner only (600)"
                                )
                    except Exception as e:
                        continue
    
    def scan_debug_code(self):
        """Scan for debug code that shouldn't be in production"""
        print("🔍 Scanning for debug code...")
        
        patterns = [
            r'console\.log\s*\(',
            r'print\s*\(',
            r'debugger;',
            r'DEBUG\s*=\s*True',
            r'debug\s*=\s*True',
            r'//\s*TODO',
            r'#\s*TODO',
            r'//\s*FIXME',
            r'#\s*FIXME',
            r'//\s*HACK',
            r'#\s*HACK'
        ]
        
        for file_path in self.get_source_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.log_issue(
                                "LOW",
                                "Debug Code",
                                file_path,
                                line_num,
                                f"Debug code found: {line.strip()[:100]}...",
                                "Remove debug code before production deployment"
                            )
            except Exception as e:
                continue
    
    def scan_cors_configuration(self):
        """Scan for insecure CORS configuration"""
        print("🔍 Scanning CORS configuration...")
        
        patterns = [
            r'allow_origins\s*=\s*\[\s*["\*"]["\*]\s*\]',
            r'Access-Control-Allow-Origin\s*:\s*\*',
            r'cors\s*\(\s*\{\s*origin\s*:\s*true',
            r'allowedOrigins\s*:\s*\[\s*["\*"]["\*]\s*\]'
        ]
        
        for file_path in self.get_source_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.log_issue(
                                "MEDIUM",
                                "CORS Configuration",
                                file_path,
                                line_num,
                                f"Insecure CORS configuration: {line.strip()[:100]}...",
                                "Restrict CORS to specific trusted domains"
                            )
            except Exception as e:
                continue
    
    def get_source_files(self, extensions: List[str] = None) -> List[Path]:
        """Get all source files in the project"""
        if extensions is None:
            extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.yaml', '.yml', '.env']
        
        files = []
        exclude_dirs = {'node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build'}
        
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in exclude_dirs):
                    continue
                
                # Check file extension
                if any(str(file_path).endswith(ext) for ext in extensions):
                    files.append(file_path)
        
        return files
    
    def run_audit(self):
        """Run complete security audit"""
        print("🛡️ Starting Security Audit for Artha AI")
        print("=" * 50)
        
        # Run all scans
        self.scan_hardcoded_secrets()
        self.scan_sql_injection()
        self.scan_xss_vulnerabilities()
        self.scan_insecure_dependencies()
        self.scan_file_permissions()
        self.scan_debug_code()
        self.scan_cors_configuration()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate security audit report"""
        print("\n" + "=" * 50)
        print("🛡️ SECURITY AUDIT REPORT")
        print("=" * 50)
        
        total_issues = len(self.issues) + len(self.warnings) + len(self.info)
        
        print(f"📊 Summary:")
        print(f"   🔴 High Severity Issues: {len(self.issues)}")
        print(f"   🟡 Medium Severity Issues: {len(self.warnings)}")
        print(f"   🔵 Low Severity Issues: {len(self.info)}")
        print(f"   📋 Total Issues: {total_issues}")
        
        if self.issues:
            print(f"\n🔴 HIGH SEVERITY ISSUES ({len(self.issues)}):")
            print("-" * 40)
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue['category']} in {issue['file']}:{issue['line']}")
                print(f"   Description: {issue['description']}")
                print(f"   Recommendation: {issue['recommendation']}")
                print()
        
        if self.warnings:
            print(f"\n🟡 MEDIUM SEVERITY ISSUES ({len(self.warnings)}):")
            print("-" * 40)
            for i, issue in enumerate(self.warnings, 1):
                print(f"{i}. {issue['category']} in {issue['file']}:{issue['line']}")
                print(f"   Description: {issue['description']}")
                print(f"   Recommendation: {issue['recommendation']}")
                print()
        
        if self.info:
            print(f"\n🔵 LOW SEVERITY ISSUES ({len(self.info)}):")
            print("-" * 40)
            for i, issue in enumerate(self.info, 1):
                print(f"{i}. {issue['category']} in {issue['file']}:{issue['line']}")
                print(f"   Description: {issue['description']}")
                print(f"   Recommendation: {issue['recommendation']}")
                print()
        
        # Security recommendations
        print("\n🛡️ SECURITY RECOMMENDATIONS:")
        print("-" * 40)
        recommendations = [
            "1. Ensure all secrets are stored in environment variables",
            "2. Use parameterized queries to prevent SQL injection",
            "3. Implement proper input validation and sanitization",
            "4. Keep dependencies updated and use exact versions",
            "5. Set restrictive file permissions on sensitive files",
            "6. Remove debug code before production deployment",
            "7. Configure CORS to allow only trusted domains",
            "8. Implement proper authentication and authorization",
            "9. Use HTTPS in production environments",
            "10. Regular security audits and penetration testing"
        ]
        
        for rec in recommendations:
            print(f"   {rec}")
        
        # Save report to file
        report_data = {
            "summary": {
                "high_severity": len(self.issues),
                "medium_severity": len(self.warnings),
                "low_severity": len(self.info),
                "total": total_issues
            },
            "issues": self.issues + self.warnings + self.info
        }
        
        report_file = self.project_root / "security_audit_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Return exit code based on severity
        if self.issues:
            print("\n❌ Security audit failed due to high severity issues!")
            return 1
        elif self.warnings:
            print("\n⚠️ Security audit completed with warnings.")
            return 0
        else:
            print("\n✅ Security audit passed!")
            return 0

def main():
    """Main function"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    auditor = SecurityAuditor(project_root)
    exit_code = auditor.run_audit()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()