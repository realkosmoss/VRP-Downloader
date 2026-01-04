from curl_cffi import requests

def make_rclone(proxy=None) -> requests.Session:
    headers = {
        "user-agent": "rclone/v1.68.2",
        "accept-encoding": "gzip",
    }

    SSL_VERIFYPEER = 64
    curl_options = {
        SSL_VERIFYPEER: 1
    }

    JA3_TEXT = (
        "771,"
        "49195-49199-49196-49200-52393-52392-49161-49171-49162-49172-"
        "156-157-47-53-49170-10-4865-4866-4867,"
        "0-11-65281-23-18-5-10-13-16-43-45-51,"
        "29-23-24-25,"
        "0"
    )

    AKAMAI_TEXT = "2:0;4:4194304;6:10485760|1073741824|0|a,m,p,s"

    session = requests.Session(
        ja3=JA3_TEXT,
        akamai=AKAMAI_TEXT,
        extra_fp={
            "tls_permute_extensions": False,
            "tls_record_size_limit": None,
            "tls_signature_algorithms": [
                "rsa_pss_rsae_sha256",
                "ecdsa_secp256r1_sha256",
                "ed25519",
                "rsa_pss_rsae_sha384",
                "rsa_pss_rsae_sha512",
                "rsa_pkcs1_sha256",
                "rsa_pkcs1_sha384",
                "rsa_pkcs1_sha512",
                "ecdsa_secp384r1_sha384",
                "ecdsa_secp521r1_sha512",
                "rsa_pkcs1_sha1",
                "ecdsa_sha1",
            ],
        },
        headers=headers,
        default_headers=False,
        curl_options=curl_options
    )

    if proxy:
        if proxy.startswith(("http://", "https://", "socks5://")):
            session.proxies = {"all": proxy}
        else:
            session.proxies = {"all": f"http://{proxy}"}

    return session