# live.tf -- cloud resources for hosting arbout on google cloud

variable google_project {}
variable google_zone { default = "us-central1-a" }
variable sql_readwrite_password {}
variable sql_readwrite_username {}
variable dns_name { default = "arbout.org." }

provider google {
  project = var.google_project
  zone = var.google_zone
}

data google_compute_network default {
  name = "default"
}

resource google_compute_global_address db-private-ip {
  name = "arbout-db-private-ip"
  purpose = "VPC_PEERING"
  address_type = "INTERNAL"
  prefix_length = 16
  network = data.google_compute_network.default.self_link
}

resource google_service_networking_connection cx {
  network = data.google_compute_network.default.self_link
  service = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.db-private-ip.name]
}

resource google_sql_database_instance arbout-master {
  name = "arbout-master"
  database_version = "POSTGRES_11"
  depends_on = [google_service_networking_connection.cx]
  settings {
    tier = "db-g1-small"
    ip_configuration {
      ipv4_enabled = false
      private_network = data.google_compute_network.default.self_link
    }
  }
}

resource google_sql_user readwrite {
  name = var.sql_readwrite_username
  instance = google_sql_database_instance.arbout-master.name
  password = var.sql_readwrite_password
}

resource google_dns_managed_zone arbout {
  name = "arbout"
  dns_name = var.dns_name
}

resource google_compute_global_address arbout-ingress-ip {
  name = "arbout-ingress-ip"
}

resource google_dns_record_set naked {
  name = google_dns_managed_zone.arbout.dns_name
  managed_zone = google_dns_managed_zone.arbout.name
  type = "A"
  ttl = 300
  rrdatas = [google_compute_global_address.arbout-ingress-ip.address]
}

output sql_ip { value = google_sql_database_instance.arbout-master.private_ip_address }
output sql_user { value = google_sql_user.readwrite.name }
output dns_ns { value = google_dns_managed_zone.arbout.name_servers }
output ingress_ip { value = google_compute_global_address.arbout-ingress-ip.address }
