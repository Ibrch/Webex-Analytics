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

erstelle .env mit deinem Token:

WEBEX_TOKEN=your_token


Manueller Test:

systemctl start webex-collector.service
