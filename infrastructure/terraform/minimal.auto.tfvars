project_prefix        = "WAFER_PROJECT"
region                = "us-east-1"
vpc_cidr              = "10.0.0.0/16"
public_subnet_cidr    = "10.0.1.0/24"
public_subnet_cidr_b  = "10.0.3.0/24"
private_subnet_cidr   = "10.0.2.0/24"

api_instance_type     = "t3.micro"
api_ami_id            = "ami-02dfbd4ff395f2a1b"

# Keep minimum footprint defaults.
enable_nat_gateway    = false
enable_alb            = false
enable_s3_vpc_endpoint = false
enable_observability  = false
use_private_api_subnet = false
api_ingress_cidr      = "0.0.0.0/0"

# Required sensitive/runtime values.
db_password           = "change-me"
api_key               = "change-me"
run_owner             = "psmballer29@gmail.com"
dvc_version_id        = "dvc-placeholder-version"
alert_email           = "psmballer29@gmail.com"
