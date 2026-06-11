#  SOC Detection Lab  Financial Threat Simulation

### SQL Injection · MITM · Session Hijacking · 
### Suricata IDS · Memory Forensics · Incident Response

![](https://img.shields.io/badge/Platform-Kali%20Linux-557C94?style=flat-square&logo=kalilinux&logoColor=white)
![](https://img.shields.io/badge/Target-Ubuntu%2024.04-E95420?style=flat-square&logo=ubuntu&logoColor=white)
![](https://img.shields.io/badge/IDS-Suricata-EF3B2D?style=flat-square)
![](https://img.shields.io/badge/Firewall-iptables-orange?style=flat-square)
![](https://img.shields.io/badge/Forensics-Volatility3-6C3483?style=flat-square)
![](https://img.shields.io/badge/Framework-OWASP%20Top%2010-000000?style=flat-square)
![](https://img.shields.io/badge/MITRE-ATT%26CK%20Mapped-red?style=flat-square)
![](https://img.shields.io/badge/Status-COMPLETE-brightgreen?style=flat-square)

---

## The Problem This Engagement Addresses

Financial institutions are the most targeted
sector in cybersecurity. The average cost of
a financial data breach exceeds $6 million.

Yet the attacks that cause most of those
breaches are not sophisticated zero-days.
They are techniques documented since 1998 
SQL injection, session hijacking, SSL stripping.

The reason organizations keep falling to
these attacks is not ignorance.

It is the gap between knowing a vulnerability
exists and understanding exactly how an attacker
exploits it end to end  and what each defensive
control actually stops.

This engagement closes that gap.

Not theoretically. With a working banking
application, real exploit execution, live IDS
alerts firing during the attack, and memory
forensics confirming attacker activity at the
RAM level.

---

## Engagement At A Glance

| | |
|---|---|
| **Environment** | VMware isolated host-only network |
| **Target** | SecureBank — simulated financial portal |
| **Red Team** | Sime Delonney Njeba (cypherguy) — Kali Linux |
| **Blue Team** | Mbaku Bertin Tengwei — Ubuntu Server |
| **Supervisor** | Engr. Taku Che Otto |
| **Institution** | University of Bamenda — NAHPI |
| **Module** | Advanced Cryptology / Network Security |
| **Date** | June 2026 |

---

## Network Topology

```
┌─────────────────────────────────────────────┐
│   ISOLATED HOST-ONLY NETWORK                │
│   192.168.100.0/24 — No internet access     │
│                                             │
│   Kali Linux          192.168.100.10        │
│   Red Team Attacker   cypherguy             │
│                                             │
│   Ubuntu Server       192.168.100.20        │
│   Target + Blue Team  Flask / Apache        │
│                                             │
│   Windows Host        192.168.100.30        │
│   Victim Workstation  Sysmon v15.20         │
└─────────────────────────────────────────────┘
```

---

## What Was Built

The SecureBank environment was built from scratch
to simulate a real financial institution network:

**Banking Application:**
A deliberately vulnerable Flask web application
with a professional banking UI — login portal,
account dashboard, transaction history, and
a SQLite customer database with five accounts.

The vulnerability: direct string concatenation
in SQL queries — the same pattern that causes
real financial breaches.

**Detection Stack:**
Seven custom Suricata IDS rules written to
detect each specific phase of the Red Team
attack — from the initial Nmap scan through
SQL injection, MITM traffic, and plaintext
credential submission.

**Victim Workstation:**
Windows host configured with Sysmon v15.20
for kernel-level forensic logging, test PII
files on the desktop, and Firefox accessing
the banking portal.

---

## Attack Objectives

The Red Team executed two of three available
objectives. Both were chosen because they
demonstrate a complete attacker kill chain
from initial access through data exfiltration
to full account takeover.

```
Objective 1:  SQL Injection — Customer Data Theft
              All five customer records exfiltrated
              including names, emails, balances,
              and plaintext passwords

Objective 2:  Session Hijacking — User Impersonation
              Mbaku's authenticated session stolen
              via ARP poisoning and SSL stripping
              Full account access from Kali without
              ever knowing his password

Objective 3:  SMB Exploitation (Not pursued)
              EternalBlue would have been blocked
              by iptables and detected by Suricata
              Documented in Section 2.5
```

---

## The Critical Findings

---

### Finding 1 — SQL Injection Exposed $91,000 in Customer Accounts

The banking portal login form was vulnerable to
classic SQL injection due to unsanitised string
concatenation in the authentication query.

**Manual payload:**
```sql
' OR '1'='1' --
```

**Result:** Authentication bypassed entirely.
All five customer records exposed with warning
banner. Account balances visible including
Mbaku's $91,000.00 account.

**Automated exploitation with sqlmap:**
The complete database was dumped in under
60 seconds using boolean-based blind injection
and UNION query techniques.

**Business impact:** In a real financial
environment this constitutes a critical breach
of GDPR and PCI-DSS requirements triggering
mandatory notification obligations and potential
regulatory fines reaching millions of dollars.

**Blue Team detection:**
```
Suricata SID 9000004 fired immediately:
"SQL INJECTION ATTEMPT on Banking Portal"
```

---

### Finding 2 — SSL Stripping Succeeded Because One Header Was Missing

TLS was correctly configured. A 4096-bit RSA
certificate was in place. The encryption was
unbroken.

The attack never needed to break it.

Bettercap positioned itself between the Windows
victim and Ubuntu server using ARP cache
poisoning. It intercepted the initial HTTP
request before TLS could be established —
serving plain HTTP to the victim while
maintaining a separate encrypted connection
to the real server.

The victim's browser never received an HSTS
header. It had no instruction to enforce HTTPS.
The downgrade succeeded silently.

Mbaku's credentials and session cookie
travelled over plain HTTP through Kali.
Captured in plaintext by Bettercap's sniffer.

**The fix was one Apache configuration line:**
```
Header always set Strict-Transport-Security
"max-age=31536000; includeSubDomains"
```

After HSTS was enabled the browser refused
any HTTP connection to the portal entirely.
The SSL stripping attack became impossible
without changing a single line of application
code.

**The lesson:** TLS does not protect a
connection that never becomes TLS. HSTS
is not optional — it is what makes TLS
enforcement actually work.

---

### Finding 3 — Memory Forensics Confirmed Attacker Activity at RAM Level

A 5GB Windows memory dump was acquired using
winpmem v4.0 during the attack window.

Volatility3 analysis confirmed at the memory
level:

```
Process list:     Sysmon64 running throughout
                  PowerShell active
                  winpmem acquisition visible

Network connections: Active connections to
                     192.168.100.20 confirmed

Command line args:  winpmem acquisition command
                    irrefutable in process memory
```

**Why this matters:** Application logs can be
deleted. SIEM alerts can be suppressed.
But RAM contents captured during an attack
cannot be altered retroactively.

Memory forensics provides the deepest available
layer of forensic evidence — the kind that
holds up in legal proceedings and regulatory
investigations.

---

## Blue Team Controls — What Worked and Why

| Control | Attack Stopped | Mechanism |
|---|---|---|
| Suricata custom rules | Detected all attack phases | 7 rules covering recon through credential theft |
| iptables default-deny | SMB exploitation blocked | DROP rule for Kali on port 445 |
| HSTS header | SSL stripping impossible | Browser enforces HTTPS unconditionally |
| Sysmon v15.20 | Full host forensic timeline | Kernel-level process and network logging |
| Immutable rsync backup | Ransomware-resistant recovery | chattr +i prevents root deletion |
| Volatility3 forensics | RAM-level attack confirmation | winpmem + symbol resolution |

---

## Attack Timeline

| Time | Actor | Action | Detection |
|---|---|---|---|
| 07:12 | Red | Nmap scan launched | Suricata SID 9000001 — NMAP SYN Scan |
| 07:20 | Red | SQL injection in browser | Suricata SID 9000004 — SQL INJECTION ATTEMPT |
| 07:20 | Red | sqlmap automated dump | Suricata SID 9000003, 9000004 |
| 08:25 | Red | Bettercap ARP spoof started | Suricata SID 9000003 — POSSIBLE MITM |
| 08:29 | Red | Mbaku credentials captured | Suricata SID 9000006 — PLAINTEXT CREDENTIALS |
| 08:29 | Red | Session cookie replayed | Sysmon Event ID 1 — process activity logged |
| 11:25 | Blue | Immutable rsync backup created | lsattr confirms chattr +i active |
| 13:54 | Blue | HSTS enabled on Apache | curl -I confirms Strict-Transport-Security |
| 15:06 | Blue | iptables default-deny applied | smbclient returns NT_STATUS_IO_TIMEOUT |

---

## Suricata Custom Rules

All seven custom detection rules written for
this engagement are in
[environment/suricata-rules/local.rules](environment/suricata-rules/local.rules)

Rules cover:
```
SID 9000001  Nmap SYN scan detection
SID 9000003  MITM high-volume forwarding traffic
SID 9000004  SQL injection attempt on port 5000
SID 9000005  SMB login attempt on port 445
SID 9000006  Plaintext credential submission
```

---

## Remediation Plan

Five concrete fixes addressing root causes:

**Fix 1 — Parameterised queries**
Eliminates SQL injection at the code level.
User input treated as data, never as SQL syntax.

**Fix 2 — HSTS preload**
Extends HSTS protection to first-time visitors
who have never received the header before.

**Fix 3 — bcrypt password hashing**
Makes cracked database hashes computationally
infeasible to reverse. MD5 cracked in seconds.
bcrypt with rounds=12 takes years.

**Fix 4 — Session management hardening**
15-minute timeout, Secure flag, HttpOnly flag,
SameSite=Strict, IP binding. Stolen cookies
expire before replay is possible.

**Fix 5 — Network segmentation**
Separate network segments for web and file
services. SMBv2 minimum, mandatory signing,
VPN-only file share access.

Full implementation detail in
[remediation-plan.md](remediation-plan.md)

---

## Challenges Documented

Every real-world obstacle encountered is
documented with root cause and resolution.

```
iptables self-lockout    Applied DROP before ACCEPT rules
                         Recovered via direct console access

Apache config conflict   Previous lab SSL config silently
                         overriding HSTS configuration
                         Found via sites-enabled/ audit

Volatility symbol error  Windows 11 build 22621 not in
                         standard symbol pack
                         Resolved via Microsoft symbol server

Memory dump truncation   /tmp partition limited to 4.2GB
                         Retransferred to /home — 5.0GB complete

Bettercap DNS failure    nameserver not configured
                         Set explicitly via resolv.conf
```

---

## What This Lab Covers

```
Red Team:
  Nmap service version scan and OS fingerprinting
  Manual SQL injection (browser-based)
  Automated SQL injection (sqlmap)
  ARP cache poisoning (Bettercap)
  SSL stripping (Bettercap HTTP proxy)
  Session cookie capture and replay
  MD5 hash cracking (John the Ripper + rockyou.txt)

Blue Team:
  Custom Suricata IDS rules (7 rules)
  iptables stateful firewall with default-deny
  HSTS and TLS certificate (Apache reverse proxy)
  Sysmon v15.20 Windows forensic logging
  Immutable rsync backup with chattr +i
  Volatility3 Windows memory forensics
  Database recovery demonstration

Documentation:
  Complete attack timeline with Suricata timestamps
  Remediation plan with production-ready code
  5 documented challenges with root causes
  38-page technical report
```

---

## How This Connects to My Other Work

The PKI methodology in this lab — 4096-bit RSA
certificate, Apache HTTPS, HSTS enforcement —
applies the same techniques built from scratch in
[Lab 5: PKI Certificate Authority](https://github.com/Deloney-code/enterprise-network-security-labs)

The Suricata detection rules extend the custom
rule writing from
[Lab 6: Enterprise Firewall & IDS](https://github.com/Deloney-code/Enterprise-Firewall-Deployment-Security-Architecture-Validation-FortiGate-NGFW)

The IAM remediation fixes — session management,
RBAC, secure cookie handling — map directly to
the access control frameworks in
[Enterprise Linux IAM Hardening](https://github.com/Deloney-code/enterprise-linux-iam-hardening)

The SQL injection attack chain represents the
offensive perspective on the same web application
vulnerabilities documented in the
[Simulated Enterprise Penetration Test](https://github.com/Deloney-code/simulated-enterprise-pentest)

---

## Repository Structure

```
securebank-red-vs-blue-lab/
│
├── README.md
├── remediation-plan.md
├── attack-timeline.md
│
├── environment/
│   ├── network-topology.md
│   ├── banking-app/
│   │   └── app.py
│   └── suricata-rules/
│       └── local.rules
│
├── red-team/
│   ├── 01-reconnaissance.md
│   ├── 02-sql-injection.md
│   ├── 03-session-hijacking.md
│   └── 04-hash-cracking.md
│
├── blue-team/
│   ├── 01-suricata-detection.md
│   ├── 02-iptables-hardening.md
│   ├── 03-hsts-tls.md
│   ├── 04-sysmon-forensics.md
│   ├── 05-backup-recovery.md
│   └── 06-volatility-memory-forensics.md
│
└── screenshots/
    └── (33 screenshots from engagement)
```

---

## Screenshots Required

```
□ 01  VMware host-only network configuration
□ 02  All three VMs connectivity confirmed
□ 03  Ubuntu services running (Apache, Flask, Samba)
□ 04  Suricata rules loaded — configuration valid
□ 05  SQLite database populated — five records
□ 06  TLS certificate generated — 4096-bit RSA
□ 07  Sysmon v15.20 installed and running
□ 08  SecureBank login portal
□ 09  Normal authenticated login — Alice only
□ 10  SQL injection payload in email field
□ 11  All five records exposed — warning banner
□ 12  sqlmap automated dump — all records
□ 13  Direct SQLite query confirming data
□ 14  Bettercap MITM active — ARP spoof enabled
□ 15  Mbaku credentials captured in plaintext
□ 16  curl session replay — Mbaku impersonated
□ 17  Full visual impersonation — dashboard
□ 18  John the Ripper — three hashes cracked
□ 19  Suricata config validated — all rules loaded
□ 20  Suricata fast.log — Nmap detection
□ 21  Suricata fast.log — MITM detection
□ 22  iptables rule set — default-deny applied
□ 23  smbclient blocked — NT_STATUS_IO_TIMEOUT
□ 24  HSTS header confirmed — curl -I output
□ 25  Sysmon v15.20 service running
□ 26  Sysmon Event ID 1 — process logs
□ 27  Immutable flag — lsattr confirmed
□ 28  Database recovered — all five records
□ 29  winpmem memory acquisition
□ 30  Memory dump — 5GB confirmed
□ 31  Volatility — process list
□ 32  Volatility — network connections
□ 33  Volatility — command line arguments
```

---

## About

**Sime Delonney Njeba (cypherguy)**
CEH v13 — Grade A | M.Sc. Cybersecurity (In Progress)
University of Bamenda — NAHPI
Centre for Cybersecurity and Mathematical Cryptology

[GitHub](https://github.com/Deloney-code) ·
[LinkedIn](https://linkedin.com/in/sime-delonney-njeba-10b89a33a)

**Mbaku Bertin Tengwei**
M.Sc. Cybersecurity (In Progress)
University of Bamenda — NAHPI

---

> All activities conducted in an isolated
> VMware host-only network with no internet
> access, strictly for academic purposes under
> the supervision of Engr. Taku Che Otto,
> University of Bamenda — NAHPI.
