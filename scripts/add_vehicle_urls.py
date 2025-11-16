import csv
from pathlib import Path

# VDP URLs provided by client (VIN is last segment of URL)
VDP_URLS = [
    "https://www.goodchev.com/used-Renton-2013-RAM-1500-SLT-1C6RR7LT8DS666620",
    "https://www.goodchev.com/used-Renton-2012-Ford-Super+Duty+F+350+DRW-LARIAT-1FT8W3DT0CEB48325",
    "https://www.goodchev.com/used-Renton-2021-Chevrolet-Silverado+4500+HD-LT-1HTKJPVK8MH316426",
    "https://www.goodchev.com/used-Renton-2022-Chevrolet-Malibu-LT-1G1ZD5ST6NF127154",
    "https://www.goodchev.com/used-Renton-2017-RAM-1500-Tradesman-3C6JR6DTXHG675130",
    "https://www.goodchev.com/used-Renton-2021-Chevrolet-Trax-LT-KL7CJLSM6MB377385",
    "https://www.goodchev.com/used-Renton-1998-Chevrolet-Camaro-Z28-2G1FP32G6W2129829",
    "https://www.goodchev.com/used-Renton-2021-Chevrolet-Trax-LT-KL7CJLSM0MB376104",
    "https://www.goodchev.com/used-Renton-2024-MINI-Cooper+S-Countryman+All4-WMZ83BR02R3R77094",
    "https://www.goodchev.com/used-Renton-2020-Chevrolet-Malibu-LT-1G1ZD5ST8LF021317",
    "https://www.goodchev.com/used-Renton-2022-Chevrolet-Equinox-LT-2GNAXKEV2N6109923",
    "https://www.goodchev.com/used-Renton-2020-Nissan-NV200+Compact+Cargo-S-3N6CM0KNXLK699903",
    "https://www.goodchev.com/used-Renton-2021-Lexus-+-RX+350-2T2AZMAA1MC207304",
    "https://www.goodchev.com/used-Renton-2022-Chevrolet-Malibu-LT-1G1ZD5STXNF141834",
    "https://www.goodchev.com/used-Renton-2024-Buick-Encore+GX-Preferred-KL4AMBS2XRB062908",
    "https://www.goodchev.com/used-Renton-2023-Kia-Soul-LX-KNDJ23AU4P7859854",
    "https://www.goodchev.com/used-Renton-2024-MINI-Cooper+S-Hardtop+4+Door-WMW53DK06R2V07064",
    "https://www.goodchev.com/used-Renton-2018-Cadillac-Escalade-Premium+Luxury-1GYS4CKJ5JR196190",
    "https://www.goodchev.com/used-Renton-2024-Chevrolet-Camaro-2SS-1G1FG1R73R0100059",
    "https://www.goodchev.com/used-Renton-2018-Ford-F+150-LARIAT-1FTEW1EP2JKC82969",
    "https://www.goodchev.com/used-Renton-2024-Chevrolet-Trax-LT-KL77LHE28RC062382",
    "https://www.goodchev.com/used-Renton-2020-Chevrolet-Malibu-LT-1G1ZD5ST9LF059364",
    "https://www.goodchev.com/used-Renton-2022-Buick-Enclave-Premium-5GAERCKW0NJ101430",
    "https://www.goodchev.com/used-Renton-2023-Mercedes+Benz-Sprinter+Cargo+Van-+-W1Y40BHY3PT139888",
    "https://www.goodchev.com/used-Renton-2022-Ford-Ranger-XL-1FTER4EH4NLD10157",
    "https://www.goodchev.com/used-Renton-2023-Chevrolet-Camaro-2SS-1G1FG1R77P0107819",
    "https://www.goodchev.com/used-Renton-2008-Dodge-Ram+2500-Laramie-3D3KS28AX8G127882",
    "https://www.goodchev.com/used-Renton-2017-Jeep-Cherokee-Altitude-1C4PJMAB8HW600566",
    "https://www.goodchev.com/used-Renton-2021-Ford-Super+Duty+F+350+SRW-Platinum-1FT8W3BT3MEC64624",
    "https://www.goodchev.com/used-Renton-2019-Buick-Envision-Premium-LRBFX3SX8KD098951",
    "https://www.goodchev.com/used-Renton-2023-Chevrolet-Suburban-Z71-1GNSKDKD1PR418168",
    "https://www.goodchev.com/used-Renton-2024-Chevrolet-Trax-LT-KL77LHE20RC084568",
    "https://www.goodchev.com/used-Renton-2019-Ford-F+150-XL-1FTEX1CP9KKD08887",
    "https://www.goodchev.com/used-Renton-2021-Chevrolet-Equinox-LT-2GNAXTEV1M6142108",
    "https://www.goodchev.com/used-Renton-2024-Ford-Maverick-XLT-3FTTW8J99RRA70407",
    "https://www.goodchev.com/used-Renton-2013-Honda-Civic+Sdn-EX-2HGFB2F80DH526466",
    "https://www.goodchev.com/used-Renton-2024-Chevrolet-Trax-LS-KL77LFE25RC126933",
    "https://www.goodchev.com/used-Renton-2022-Chevrolet-Trailblazer-LT-KL79MPSL7NB084032",
    "https://www.goodchev.com/used-Renton-2023-Kia-Sorento+Hybrid-EX-KNDRHDLG6P5171171",
    "https://www.goodchev.com/used-Renton-2024-Volkswagen-Taos-S-3VV5X7B25RM037727",
    "https://www.goodchev.com/used-Renton-2024-Kia-Sportage-X+Line-5XYK6CDF3RG160100",
    "https://www.goodchev.com/used-Renton-2021-Cadillac-XT6-Premium+Luxury-1GYKPFRS7MZ137735",
    "https://www.goodchev.com/used-Renton-2024-Chevrolet-Trax-LS-KL77LFE26RC224482",
    "https://www.goodchev.com/used-Renton-2015-Chevrolet-Sonic-LT-1G1JC5SG3F4126012",
    "https://www.goodchev.com/used-Renton-2023-Dodge-Charger-SXT-2C3CDXBG2PH592452",
    "https://www.goodchev.com/used-Renton-2021-Hyundai-Palisade-SEL-KM8R4DHE7MU298429",
    "https://www.goodchev.com/used-Renton-2023-Chevrolet-Camaro-ZL1-1G1FK1R69P0138110",
    "https://www.goodchev.com/used-Renton-2018-GMC-Sierra+3500+HD+Chassis+Cab-+-1GD32VCY7JF264915",
    "https://www.goodchev.com/used-Renton-2016-RAM-1500-Rebel-1C6RR7YT7GS397426",
    "https://www.goodchev.com/used-Renton-2019-Chevrolet-Trax-LT-3GNCJPSB5KL154685",
    "https://www.goodchev.com/used-Renton-2023-Toyota-Highlander-L-5TDKDRBH0PS512417",
    "https://www.goodchev.com/used-Renton-2021-Ford-ESCAPE-+-1FMCU9H91MUA75809",
    "https://www.goodchev.com/used-Renton-2022-Kia-Sorento-SX+Prestige-5XYRK4LF2NG077303",
    "https://www.goodchev.com/used-Renton-2020-Mercedes+Benz-+-GLE+350-4JGFB4KB0LA078511",
    "https://www.goodchev.com/used-Renton-2023-RIVIAN-R1S-Launch+Edition-7PDSGABL7PN004327",
    "https://www.goodchev.com/used-Renton-2021-Chevrolet-Colorado-ZR2-1GCRTEE17M1209927",
    "https://www.goodchev.com/used-Renton-2023-Chevrolet-Express+Cargo+2500-WT-1GCWGAFP8P1214240",
    "https://www.goodchev.com/used-Renton-2023-Chevrolet-Express+Cargo+2500-WT-1GCWGAFPXP1214224",
    "https://www.goodchev.com/used-Renton-2023-GMC-Savana+Cargo+2500-Work+Van-1GTW7AFP5P1201445",
    "https://www.goodchev.com/used-Renton-2023-GMC-Savana+Cargo+2500-Work+Van-1GTW7AFP5P1216690",
    "https://www.goodchev.com/used-Renton-2025-Chevrolet-Equinox-LT-3GNAXHEG4SL175417",
    "https://www.goodchev.com/used-Renton-2018-Chevrolet-Volt-LT-1G1RC6S54JU151145",
    "https://www.goodchev.com/used-Renton-2024-Chevrolet-Colorado-ZR2-1GCPTFEK9R1113455",
    "https://www.goodchev.com/used-Renton-2025-Chevrolet-Equinox+EV-RS-3GN7DSRP6SS140913",
    "https://www.goodchev.com/used-Renton-2019-Buick-Envision-Preferred-LRBFXBSA7KD146008",
    "https://www.goodchev.com/used-Renton-2020-Hyundai-Sonata-Limited-5NPEH4J28LH021739",
    "https://www.goodchev.com/used-Renton-2022-Hyundai-Elantra-Limited-5NPLP4AG6NH059477",
    "https://www.goodchev.com/used-Renton-2022-Volvo-XC60-Momentum-YV4L12RK3N1021126",
    "https://www.goodchev.com/used-Renton-2021-GMC-Sierra+1500-AT4-1GTU9EET3MZ435443",
    "https://www.goodchev.com/used-Renton-2021-Jeep-Wrangler-Willys-1C4GJXAG5MW842447",
    "https://www.goodchev.com/used-Renton-2020-Chevrolet-Traverse-Premier-1GNEVKKW7LJ237966",
    "https://www.goodchev.com/used-Renton-2025-Nissan-ARIYA-ENGAGE-JN8AF0BE1SM462918",
    "https://www.goodchev.com/used-Renton-2019-Volkswagen-Arteon-SEL-WVWDR7AN3KE027452",
    "https://www.goodchev.com/used-Renton-2023-Dodge-Challenger-GT-2C3CDZJG6PH503639",
    "https://www.goodchev.com/used-Renton-2020-Ford-Ranger-XLT-1FTER4FH1LLA40090",
    "https://www.goodchev.com/used-Renton-2021-Honda-Civic+Sedan-EX-19XFC1F34ME209358",
    "https://www.goodchev.com/used-Renton-2018-Volkswagen-Golf+GTI-S-3VW447AU5JM265041",
    "https://www.goodchev.com/used-Renton-2016-Chevrolet-Corvette+Stingray-1LT-1G1YB2D75G5107874",
    "https://www.goodchev.com/used-Renton-2022-Kia-Sorento+Plug+In+Hybrid-SX+Prestige-KNDRMDLH1N5077989",
    "https://www.goodchev.com/used-Renton-2022-RAM-1500+Classic-Warlock-1C6RR7LG4NS204026",
    "https://www.goodchev.com/used-Renton-2024-Jeep-Grand+Cherokee+L-Limited-1C4RJKBG7R8934181",
    "https://www.goodchev.com/used-Renton-2018-Ford-F+150-XLT-1FTEW1E59JKD82307",
    "https://www.goodchev.com/used-Renton-2022-Ford-E+Series+Cutaway-+-1FDWE3FK0NDC12771",
    "https://www.goodchev.com/used-Renton-2022-Porsche-Macan-+-WP1AA2A50NLB03883",
    "https://www.goodchev.com/used-Renton-2018-Audi-TT+RS-+-WUACSAFV2J1902017",
    "https://www.goodchev.com/used-Renton-2021-Nissan-Altima-25+SR-1N4BL4CV4MN415254",
    "https://www.goodchev.com/used-Renton-2015-Chevrolet-Silverado+3500+HD-LTZ-1GC4K0C89FF533418",
    "https://www.goodchev.com/used-Renton-2024-Chrysler-Pacifica-Touring-2C4RC1FG2RR116795",
    "https://www.goodchev.com/used-Renton-2024-Dodge-Durango-RT+Plus-1C4SDJCT0RC185588",
    "https://www.goodchev.com/used-Renton-2025-Volkswagen-Atlas-20T+SE+wTechnology-1V2HR2CA1SC518210",
    "https://www.goodchev.com/used-Renton-2017-Mercedes+Benz-Metris+Cargo+Van-+-WD3PG2EA0H3235767",
    "https://www.goodchev.com/used-Renton-2025-Chevrolet-Trax-2RS-KL77LJEP9SC121318",
    "https://www.goodchev.com/used-Renton-2025-Honda-Civic+Si-+-2HGFE1E55SH473897",
    "https://www.goodchev.com/used-Renton-2019-Tesla-Model+X-Long+Range+AWD-5YJXCDE22KF160957",
    "https://www.goodchev.com/used-Renton-2018-Ford-F+150-XLT-1FTEW1EG9JKF80399",
    "https://www.goodchev.com/used-Renton-2018-+-Mazda+CX+5-Touring-JM3KFBCM5J0325219",
    "https://www.goodchev.com/used-Renton-2018-Ford-Escape-SE-1FMCU9GD1JUB14836",
    "https://www.goodchev.com/used-Renton-2013-Ford-F+150-XL-1FTFW1CT8DKF38735",
    "https://www.goodchev.com/used-Renton-2019-BMW-X4-M40i-5UXUJ5C56KLA93600",
    "https://www.goodchev.com/used-Renton-2024-Kia-Telluride-S-5XYP6DGC4RG489109",
    "https://www.goodchev.com/used-Renton-2024-Chevrolet-Corvette+Stingray-2LT-1G1YB2D45R5107107",
    "https://www.goodchev.com/used-Renton-2020-Volkswagen-Jetta-SEL+Premium-3VWGB7BU4LM069645",
    "https://www.goodchev.com/used-Renton-2024-Chevrolet-Trax-LT-KL77LHE24RC041500",
    "https://www.goodchev.com/used-Renton-2025-Hyundai-Tucson-SEL-5NMJBCDE6SH495491",
    "https://www.goodchev.com/used-Renton-2019-Tesla-Model+3-Long+Range-5YJ3E1EB9KF493664",
    "https://www.goodchev.com/used-Renton-2023-Honda-Ridgeline-RTL-5FPYK3F58PB018640",
    "https://www.goodchev.com/used-Renton-2024-Subaru-WRX-+-JF1VBAB63R9801026",
    "https://www.goodchev.com/used-Renton-2021-Acura-TLX-wA+Spec+Package-19UUB6F55MA000756",
    "https://www.goodchev.com/used-Renton-2022-Ford-Super+Duty+F+350+DRW-XL-1FD8W3HT3NEC92525",
    "https://www.goodchev.com/used-Renton-2024-RAM-3500-Big+Horn-3C63RRHL7RG289450",
    "https://www.goodchev.com/used-Renton-2021-Tesla-Model+3-Standard+Range+Plus-5YJ3E1EA2MF027391",
    "https://www.goodchev.com/used-Renton-2025-Chevrolet-Blazer+EV-SS-3GNKDERL8SS136788",
    "https://www.goodchev.com/used-Renton-2015-Toyota-RAV4-LE-2T3BFREV7FW250002",
]

def extract_vin_from_url(url: str) -> str:
    """Extract VIN (last segment) from GoodChev URL"""
    return url.split('-')[-1]

def main():
    # Create VIN to URL mapping
    vin_to_url = {}
    for url in VDP_URLS:
        vin = extract_vin_from_url(url)
        vin_to_url[vin] = url
    
    print(f"📊 Loaded {len(vin_to_url)} VDP URLs")
    print(f"   Sample VIN→URL mapping:")
    for vin, url in list(vin_to_url.items())[:3]:
        print(f"   {vin} → {url}")
    print()
    
    # Read original CSV
    input_csv = Path("backend/data/goodchev_renton_inventory.csv")
    
    with input_csv.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        
        # Add Vehicle URL column if not present
        if "Vehicle URL" not in fieldnames:
            fieldnames.append("Vehicle URL")
        
        rows = []
        matched_count = 0
        
        for row in reader:
            vin = (row.get("VIN") or "").strip()
            
            # Match VIN to URL
            if vin in vin_to_url:
                row["Vehicle URL"] = vin_to_url[vin]
                matched_count += 1
            else:
                row["Vehicle URL"] = ""
            
            rows.append(row)
    
    # Write updated CSV
    with input_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Updated CSV: {input_csv}")
    print(f"   Total vehicles: {len(rows)}")
    print(f"   Matched with URLs: {matched_count}")
    print(f"   No URL found: {len(rows) - matched_count}")
    print()
    print(f"📝 New column 'Vehicle URL' added")
    print(f"   Ready to run photo scraper!")

if __name__ == "__main__":
    main()
