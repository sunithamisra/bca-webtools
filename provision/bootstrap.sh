#!/usr/bin/env bash
# ----------------------------------------
# https://github.com/Divi/VagrantBootstrap
# ----------------------------------------
# Include parameteres file
# ------------------------
source /vagrant/.vagrant_bootstrap/parameters.sh
# Update the box release repositories
# -----------------------------------
apt-get update
