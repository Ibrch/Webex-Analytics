# Webex Analytics

Automatisierter Webex CDR Collector auf Ubuntu 24.04 mit Python, DuckDB, Parquet, systemd, Ansible und Vagrant für lokale testing.
         

# Komponenten

    Ubuntu 24.04
    Python 3.12
    Python Virtual Environment
    Webex CDR API
    DuckDB
    Parquet mit ZSTD-Kompression
    systemd Service + Timer
    Ansible
    Vagrant + VirtualBox



# Collector
app/collector.py:

Ruft Webex CDR-Daten über die Webex API ab.

Verwendet ein Zeitfenster von 30 Minuten mit 2 Minuten Verzögerung.

Speichert die Raw API Response als JSON.

Importiert CDRs in DuckDB.

Verhindert Duplikate anhand der report_id.

Aktualisiert data/parquet/cdr.parquet.


# Lokale Entwicklung
Voraussetzungen:

Vagrant
VirtualBox

Konfiguration:

Der Webex API Token wird über .env bereitgestellt:

WEBEX_TOKEN=your_token


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

Die DuckDB-Struktur wird dagegen über Ansible aus
ansible/roles/webex-analytics/files/schema.sql
initialisiert.


