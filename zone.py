import dns.resolver
import dns.query
import dns.message
import dns.exception
import ipaddress

def find_authoritative_nameservers(domain):
    # find nameservers for a domain
    try:
        ns_records = dns.resolver.resolve(domain, dns.rdatatype.NS)
        nameservers = [str(ns.target) for ns in ns_records]
        return nameservers
    except dns.resolver.NXDOMAIN:
        print(f"Domain {domain} not found.")
        return None
    except dns.resolver.NoAnswer:
        print(f"No authoritative nameservers found for {domain}.")
        return None

def get_ip_address(nameserver):
    # get the IP address of a nameserver
    try:
        a_records = dns.resolver.resolve(nameserver, rdtype=dns.rdatatype.A)
        if a_records:
            return a_records[0].to_text()
        aaaa_records = dns.resolver.resolve(nameserver, rdtype=dns.rdatatype.AAAA)
        if aaaa_records:
            return aaaa_records[0].to_text()
        print(f"No A or AAAA records found for nameserver {nameserver}.")
        return None
    except dns.resolver.NXDOMAIN:
        print(f"Nameserver {nameserver} not found.")
        return None
    except dns.resolver.NoAnswer:
        print(f"No A or AAAA records found for nameserver {nameserver}.")
        return None

def perform_zone_transfer(domain, target_nameserver):
    # perform a DNS zone transfer
    ip_address = get_ip_address(target_nameserver)
    if not ip_address:
        return None

    try:
        transfer_request = dns.message.make_query(domain, dns.rdatatype.AXFR)
        response = dns.query.tcp(transfer_request, ip_address, timeout=5)
        answer_section = response.answer
        zone_data = ""
        for rrset in answer_section:
            for item in rrset.items:
                zone_data += str(item)
        return zone_data

    except dns.exception.DNSException as e:
        print(f"Error during zone transfer for {domain} from {target_nameserver} ({ip_address}): {e}")
        return None

def main():
    # Read the list of domains
    with open("domain_list.txt", "r") as file:
        domains = file.read().splitlines()

    # Iterate through each domain
    for target_domain in domains:
        print(f"\nTesting domain: {target_domain}")

        # Find nameservers
        nameservers = find_authoritative_nameservers(target_domain)

        if not nameservers:
            continue

        # Use the first authoritative nameserver
        target_nameserver = nameservers[0]

        # Perform the zone transfer
        zone_data = perform_zone_transfer(target_domain, target_nameserver)

        # results
        if zone_data:
            print(f"Zone transfer successful for {target_domain}")
            
        else:
            print(f"Zone transfer failed for {target_domain}")

if __name__ == "__main__":
    main()
