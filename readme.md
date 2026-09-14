# Webex Analytics

Automatisierter Webex CDR Collector auf Ubuntu 24.04 mit Python, DuckDB, Parquet, systemd, Ansible und Vagrant.

# Architektur
Vagrant
└── VirtualBox
    └── Ubuntu 24.04
        └── Ansible
            └── /opt/webex-analytics
                ├── app/
                │   └── collector.py
                ├── data/
                │   ├── raw/
                │   └── parquet/
                ├── state/
                │   └── webex.duckdb
                ├── venv/
                └── .env

# Komponenten
Ubuntu 24.04
Python 3.12
Python virtual environment
Webex CDR API
DuckDB
Parquet mit ZSTD-Kompression
systemd Service + Timer
Ansible
Vagrant + VirtualBox
Collector

# app/collector.py:

Ruft Webex CDR-Daten über die Webex API ab.
Verwendet ein Zeitfenster von 30 Minuten mit 2 Minuten Verzögerung.
Speichert die Raw API Response als JSON.
Importiert CDRs in DuckDB.
Verhindert Duplikate anhand der report_id.
Aktualisiert data/parquet/cdr.parquet.

# Projektstruktur
.
├── app/
│   └── collector.py
├── ansible/
│   ├── site.yml
│   └── roles/
│       └── webex-analytics/
│           ├── files/
│           │   └── schema.sql
│           └── tasks/
│               └── main.yml
├── systemd/
│   ├── webex-collector.service
│   └── webex-collector.timer
├── requirements.txt
├── .env.example
├── .gitignore
└── Vagrantfile


# Lokale Entwicklung

Voraussetzungen:

Vagrant
VirtualBox

VM erstellen:

vagrant up


Bestehende VM neu provisionieren:

vagrant provision


VM betreten:

vagrant ssh

Konfiguration

Der Webex API Token wird über .env bereitgestellt:

WEBEX_TOKEN=your_token


Die Datei .env wird nicht in Git gespeichert.

Aktuell wird .env manuell auf der VM angelegt.

systemd

Service:

webex-collector.service


Timer:

webex-collector.timer


Der Timer startet den Collector alle 5 Minuten.

Status prüfen:

systemctl status webex-collector.timer


Timer anzeigen:

systemctl list-timers --all | grep webex


Logs:

journalctl -u webex-collector.service -n 50 --no-pager


Manueller Test:

systemctl start webex-collector.service

Daten

Runtime-Daten werden nicht in Git versioniert.

Ignoriert werden:

.env
venv/
data/raw/
data/parquet/
state/
.vagrant/


Die DuckDB-Struktur wird dagegen über Ansible aus
ansible/roles/webex-analytics/files/schema.sql
initialisiert.

Vagrant dient ausschließlich als lokale Entwicklungsumgebung.
