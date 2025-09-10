# This filter takes a bunch of acm secrets that represent the remote clusters
# (Usually it is all secrets that are labeled with:
# "apps.open-cluster-management.io/secret-type=acm-cluster")

# These secrets are usually in the form of:
# data:
#   config: ewogIC...
#   name: bWNnLW9uZQ==
#   server: aHR0cHM6Ly9hcGkubWNnLW9uZS5ibHVlcHJpbnRzLnJoZWNvZW5nLmNvbTo2NDQz

# The filter parses the secret (name, server, config) and returns a dictionary of secrets in the
# following form:
# <acm-name>:
#   bearerToken: <bearerToken to access remote cluster>

import json
from base64 import b64decode


# These are the labels of an acm secret
# labels:
#   apps.open-cluster-management.io/cluster-name: local-cluster
#   apps.open-cluster-management.io/cluster-server: api.mcg-hub.blueprints.rhecoeng.com
#   apps.open-cluster-management.io/secret-type: acm-cluster
def get_cluster_name(secret):
    if "metadata" in secret and "labels" in secret["metadata"]:
        return secret["metadata"]["labels"].get(
            "apps.open-cluster-management.io/cluster-name", None
        )
    return None


def parse_acm_secrets(secrets):
    ret = {}
    for secret in secrets:
        cluster = get_cluster_name(secret)
        if cluster is None:
            continue

        ret[cluster] = {}
        config = b64decode(secret["data"]["config"])
        parsed_config = json.loads(config)
        ret[cluster]["bearerToken"] = parsed_config["bearerToken"]

    return ret


class FilterModule:

    def filters(self):
        return {"parse_acm_secrets": parse_acm_secrets}
