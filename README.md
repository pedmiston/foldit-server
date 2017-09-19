# Foldit server

This repo contains Ansible playbooks for configuring a server to scrape solution data from <analytics.fold.it>.

![](img/architecture.png)

**Data science workflow.**  
Solutions are scraped into a MySQL database. The workflow is organized around Ansible playbooks.

1. `ansible-playbook setup-foldit-server.yml`: Configure the `foldit` server (e.g., set up the MySQL database).
1. `ansible-playbook schedule-scrape.yml`: Set a cron job on the FoldIt server for when to run the `scrape.yml` playbook.
1. `ansible-playbook scrape.yml`: Scrape new solutions from <analytics.fold.it>.

**Analyzing the data.**  
To analyze the data, install the R package "pedmiston/foldit-data" from GitHub.  
https://github.com/pedmiston/foldit-data

```R
#
devtools::install_github("pedmiston/foldit-data")
```
