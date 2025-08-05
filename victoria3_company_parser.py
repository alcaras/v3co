#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria 3 Company Data Parser v6 - Final: All Bugs Fixed
- Fixed prestige good icons with proper alt text
- Fixed table horizontal overflow
- Consistent company name column width across tables
- Columns ordered by building usage frequency
- Company cards show formation requirements properly
- Country flags working correctly
"""

import os
import re
# from pathlib import Path  # Not available in Python 2.7
from collections import defaultdict, Counter
import json

class Victoria3CompanyParserV6Final:
    def __init__(self, game_directory="game", use_subject_relationships=False):
        self.game_directory = game_directory
        self.use_subject_relationships = use_subject_relationships  # Flag to control subject relationship usage
        self.company_types_dir = os.path.join(game_directory, "company_types")
        self.states_file = os.path.join(game_directory, "history", "states", "00_states.txt")
        self.diplomacy_file = os.path.join(game_directory, "history", "diplomacy", "00_subject_relationships.txt")
        self.prestige_goods_dir = os.path.join(game_directory, "prestige_goods", "00_prestige_goods.txt")
        self.wiki_file = "wiki/flavored.wiki"
        
        self.companies = {}
        self.all_buildings = set()
        self.prestige_goods = {}
        self.state_to_country = {}
        self.subject_relationships = {}  # Maps subject -> overlord
        self.wiki_companies = {}
        
        self.setup_building_to_goods()
        self.setup_country_flags()
        self.setup_prestige_good_names()
        self.setup_company_icon_mapping()
        
        # Parse data
        self.parse_state_to_country_mappings()
        if self.use_subject_relationships:
            self.parse_subject_relationships()
        self.parse_wiki_data()
        self.parse_prestige_goods()
        self.parse_all_companies()

    def setup_building_to_goods(self):
        """Map building types to their primary goods for icon selection"""
        self.building_to_goods = {
            'building_wheat_farm': 'grain',
            'building_rice_farm': 'grain', 
            'building_maize_farm': 'grain',
            'building_millet_farm': 'grain',
            'building_rye_farm': 'grain',
            'building_cattle_ranch': 'meat',
            'building_pig_farm': 'meat',
            'building_livestock_ranch': 'meat',
            'building_dairy_farm': 'dairy',
            'building_fishing_wharf': 'fish',
            'building_coffee_plantation': 'coffee',
            'building_tea_plantation': 'tea',
            'building_tobacco_plantation': 'tobacco',
            'building_cotton_plantation': 'fabric',
            'building_silk_plantation': 'silk',
            'building_dye_plantation': 'dye',
            'building_opium_plantation': 'opium',
            'building_sugar_plantation': 'sugar',
            'building_banana_plantation': 'fruit',
            'building_rubber_plantation': 'rubber',
            'building_logging_camp': 'wood',
            'building_coal_mine': 'coal',
            'building_iron_mine': 'iron',
            'building_lead_mine': 'lead',
            'building_sulfur_mine': 'sulfur',
            'building_gold_mine': 'gold',
            'building_oil_rig': 'oil',
            'building_whaling_station': 'meat',
            'building_food_industry': 'groceries',
            'building_textile_mills': 'fabric',
            'building_furniture_manufactories': 'furniture',
            'building_furniture_manufacturies': 'furniture',
            'building_paper_mills': 'paper',
            'building_steel_mills': 'steel',
            'building_tooling_workshops': 'tools',
            'building_chemical_plants': 'fertilizer',
            'building_synthetics_plants': 'dye',
            'building_synthetic_dye_plants': 'dye',
            'building_synthetic_fabric_plants': 'fabric',
            'building_glassworks': 'glass',
            'building_ceramics_workshops': 'porcelain',
            'building_distilleries': 'liquor',
            'building_breweries': 'liquor',
            'building_tobacco_manufactories': 'tobacco',
            'building_sugar_refineries': 'sugar',
            'building_tea_estates': 'tea',
            'building_coffee_estates': 'coffee',
            'building_arms_industry': 'small_arms',
            'building_munition_plants': 'ammunition',
            'building_explosives_factory': 'explosives',
            'building_artillery_foundries': 'artillery',
            'building_motor_industry': 'engines',
            'building_automotive_industry': 'automobiles',
            'building_shipyards': 'clipper_transports',
            'building_railway': 'transportation',
            'building_port': 'transportation',
            'building_trade_center': 'services',
            'arts_academy': 'fine_art',
            # Missing mappings for prestige goods
            'building_vineyard_plantation': 'wine',
            'building_military_shipyards': 'ironclads',
            'building_shipyards': 'steamers',  # Override clipper_transports
            'building_electrics_industry': 'telephones',
            'building_textile_mills': 'clothes',  # Override fabric  
            'building_logging_camp': 'hardwood',  # Override wood
            'building_port': 'merchant_marine'  # Override transportation
        }

    def setup_country_flags(self):
        """Map country codes to flag emojis"""
        self.country_flags = {
            'USA': '🇺🇸', 'GBR': '🇬🇧', 'FRA': '🇫🇷', 'DEU': '🇩🇪', 'RUS': '🇷🇺',
            'AUS': '🇦🇹', 'ITA': '🇮🇹', 'SPA': '🇪🇸', 'POR': '🇵🇹', 'NET': '🇳🇱',
            'BEL': '🇧🇪', 'SWI': '🇨🇭', 'DEN': '🇩🇰', 'SWE': '🇸🇪', 'NOR': '🇳🇴',
            'JAP': '🇯🇵', 'CHI': '🇨🇳', 'KOR': '🇰🇷', 'SIA': '🇹🇭', 'BUR': '🇲🇲',
            'ARG': '🇦🇷', 'BRZ': '🇧🇷', 'CHL': '🇨🇱', 'BOL': '🇧🇴', 'PEU': '🇵🇪',
            'COL': '🇨🇴', 'CLM': '🇨🇴', 'VNZ': '🇻🇪', 'ECU': '🇪🇨', 'URU': '🇺🇾', 'PRG': '🇵🇾',
            'MEX': '🇲🇽', 'CUB': '🇨🇺', 'HAI': '🇭🇹', 'CAN': '🇨🇦', 'TUR': '🇹🇷',
            'EGY': '🇪🇬', 'PER': '🇮🇷', 'AFG': '🇦🇫', 'ETH': '🇪🇹', 'MAD': '🇲🇬',
            'SAF': '🇿🇦', 'MOR': '🇲🇦', 'TUN': '🇹🇳', 'GRE': '🇬🇷', 'SER': '🇷🇸',
            'BUL': '🇧🇬', 'ROM': '🇷🇴', 'HUN': '🇭🇺', 'POL': '🇵🇱', 'FIN': '🇫🇮',
            'IND': '🇮🇳', 'BIC': '🇮🇳', 'AST': '🇦🇺', 'NZL': '🇳🇿', 'PHI': '🇵🇭',
            'DEI': '🇮🇩', 'MUG': '🇮🇳', 'NEP': '🇳🇵', 'BHU': '🇧🇹', 'CEY': '🇱🇰',
            'SIK': '🇮🇳', 'TIB': '🏴', 'MON': '🇲🇳', 'MAL': '🇲🇾', 'SIN': '🇸🇬',
            'PRU': '🇩🇪', 'BAV': '🇩🇪', 'WUR': '🇩🇪', 'SAX': '🇩🇪', 'HAN': '🇩🇪',
            'BAD': '🇩🇪', 'HES': '🇩🇪', 'OLD': '🇩🇪', 'MEC': '🇩🇪', 'SAR': '🇮🇹',
            'SIC': '🇮🇹', 'PAP': '🇮🇹', 'TUS': '🇮🇹', 'MOD': '🇮🇹', 'PAR': '🇮🇹',
            'LUC': '🇮🇹', 'VEN': '🇮🇹', 'TWO': '🇮🇹', 'LUX': '🇱🇺', 'WAL': '🇷🇴',
            'MOL': '🇷🇴', 'SER': '🇷🇸', 'MON': '🇲🇪', 'BOS': '🇧🇦', 'CRO': '🇭🇷',
            'LAN': '🇨🇳', 'KOK': '🇺🇿', 'SOK': '🇳🇬', 'BIC': '🇮🇳', 'DAI': '🇻🇳',
            'SIA': '🇹🇭', 'BUR': '🇲🇲', 'NSW': '🇦🇺', 'CLM': '🇨🇴', 'KUN': '🇦🇫',
            'OZH': '🇰🇿', 'ARB': '🇸🇦', 'CON': '🇫🇷', 'AST': '🇦🇺'
        }
        
    def get_country_flag(self, country_code):
        """Get flag emoji for a country code"""
        return self.country_flags.get(country_code, '')
    
    def get_country_name(self, country_code):
        """Get full country name for a country code"""
        country_names = {
            'USA': 'United States',
            'GBR': 'Great Britain',
            'FRA': 'France',
            'DEU': 'Germany',
            'PRU': 'Prussia',
            'AUS': 'Austria-Hungary',
            'RUS': 'Russia',
            'JAP': 'Japan',
            'CHI': 'China',
            'ITA': 'Italy',
            'SAR': 'Sardinia-Piedmont',
            'SPA': 'Spain',
            'TUR': 'Turkey',
            'EGY': 'Egypt',
            'PER': 'Persia',
            'SWE': 'Sweden',
            'NOR': 'Norway',
            'DEN': 'Denmark',
            'NET': 'Netherlands',
            'BEL': 'Belgium',
            'SWI': 'Switzerland',
            'BAD': 'Baden',
            'SAX': 'Saxony',
            'BAV': 'Bavaria',
            'WUR': 'Württemberg',
            'HAN': 'Hanover',
            'HES': 'Hesse',
            'OLD': 'Oldenburg',
            'MEC': 'Mecklenburg',
            'MEX': 'Mexico',
            'BRZ': 'Brazil',
            'ARG': 'Argentina',
            'CHL': 'Chile',
            'BOL': 'Bolivia',
            'NPU': 'Peru-Bolivia',
            'VNZ': 'Venezuela',
            'CLM': 'Gran Colombia',
            'COL': 'Colombia',
            'PRG': 'Paraguay',
            'URU': 'Uruguay',
            'CRI': 'Costa Rica',
            'GUA': 'Guatemala',
            'HAI': 'Haiti',
            'DOM': 'Dominican Republic',
            'POR': 'Portugal',
            'GRE': 'Greece',
            'SER': 'Serbia',
            'ROM': 'Romania',
            'WAL': 'Wallachia',
            'MOL': 'Moldavia',
            'BUL': 'Bulgaria',
            'ALB': 'Albania',
            'MON': 'Montenegro',
            'BOS': 'Bosnia',
            'CRO': 'Croatia',
            'HUN': 'Hungary',
            'POL': 'Poland',
            'FIN': 'Finland',
            'LIT': 'Lithuania',
            'LAT': 'Latvia',
            'EST': 'Estonia',
            'UKR': 'Ukraine',
            'BYE': 'Belarus',
            'GEO': 'Georgia',
            'ARM': 'Armenia',
            'AZB': 'Azerbaijan',
            'KAZ': 'Kazakhstan',
            'UZB': 'Uzbekistan',
            'TUR': 'Turkestan',
            'KOK': 'Kokand',
            'KHI': 'Khiva',
            'BUK': 'Bukhara',
            'AFG': 'Afghanistan',
            'KUN': 'Afghanistan',
            'IND': 'India',
            'BIC': 'British India',
            'MYS': 'Mysore',
            'HYD': 'Hyderabad',
            'PNJ': 'Punjab',
            'NEP': 'Nepal',
            'BHU': 'Bhutan',
            'SIA': 'Siam',
            'BUR': 'Burma',
            'DAI': 'Dai Nam',
            'KOR': 'Korea',
            'ETH': 'Ethiopia',
            'EGY': 'Egypt',
            'SUD': 'Sudan',
            'MAD': 'Madagascar',
            'ZAN': 'Zanzibar',
            'OMN': 'Oman',
            'PER': 'Persia',
            'ARB': 'Arabian Peninsula',
            'MOR': 'Morocco',
            'TUN': 'Tunisia',
            'TRI': 'Tripolitania',
            'CYR': 'Cyrenaica',
            'LIB': 'Liberia',
            'HAW': 'Hawaii',
            'TEX': 'Texas',
            'CAL': 'California',
            'DES': 'Deseret',
            'CAN': 'Canada',
            'HBC': 'Hudson Bay Company',
            'NSW': 'New South Wales',
            'VIC': 'Victoria',
            'QLD': 'Queensland',
            'WAS': 'Western Australia',
            'SAS': 'South Australia',
            'TAS': 'Tasmania',
            'NZL': 'New Zealand',
            'SAF': 'South Africa',
            'NAT': 'Natal',
            'ORA': 'Orange Free State',
            'TRV': 'Transvaal',
            'ZUL': 'Zululand',
            'XHO': 'Xhosa',
            'SOT': 'Basutoland',
            'SWZ': 'Swaziland',
            'BOT': 'Botswana',
            'NAM': 'Namibia',
            'ANG': 'Angola',
            'MOZ': 'Mozambique',
            'CON': 'Congo',
            'CAM': 'Cameroon',
            'NIG': 'Nigeria',
            'GHA': 'Gold Coast',
            'SEN': 'Senegal',
            'GAM': 'Gambia',
            'GUB': 'Guinea-Bissau',
            'GUI': 'Guinea',
            'SIE': 'Sierra Leone',
            'LBR': 'Liberia',
            'IVO': 'Ivory Coast',
            'VOL': 'Upper Volta',
            'MAL': 'Mali',
            'NIG': 'Niger',
            'CHA': 'Chad',
            'CAR': 'Central African Republic',
            'GAB': 'Gabon',
            'EQG': 'Equatorial Guinea',
            'STP': 'São Tomé and Príncipe',
            'CPV': 'Cape Verde',
            'PHI': 'Philippines',
            'DEI': 'Dutch East Indies',
            'BRU': 'Brunei',
            'JOH': 'Johor',
            'ATJ': 'Aceh',
            'BAL': 'Bali',
            'LOB': 'Lombok',
            'BSK': 'Batak',
            'LAN': 'Lanfang',
            'SAK': 'Sarawak',
            'SAB': 'North Borneo',
            'PNG': 'Papua New Guinea',
            'SOL': 'Solomon Islands',
            'VAN': 'Vanuatu',
            'FIJ': 'Fiji',
            'SAM': 'Samoa',
            'TON': 'Tonga',
            'TAH': 'Tahiti',
            'PNI': 'Pernambuco',
            'LUX': 'Luxembourg',
            'SIC': 'Sicily',
            'PAP': 'Papal States',
            'TUS': 'Tuscany',
            'MOD': 'Modena',
            'PAR': 'Parma',
            'LUC': 'Lucca',
            'VEN': 'Venice',
            'LOM': 'Lombardy',
            'SAV': 'Savoy',
            'OZH': 'Kazakh Khanate',
            'LAN': 'Lanfang Republic',
            'KOK': 'Kokand',
            'SOK': 'Sokoto Caliphate',
            'BIC': 'British India',
            'DAI': 'Dai Nam',
            'SIA': 'Siam',
            'BUR': 'Burma',
            'NSW': 'New South Wales',
            'CLM': 'Gran Colombia',
            'KUN': 'Kunduz',
            'ARB': 'Arabia',
            'CON': 'French Congo',
            'AST': 'Australia'
        }
        return country_names.get(country_code, country_code)  # Fallback to country code if not found
    
    def get_company_display_name(self, company_name):
        """Get a better display name for the company"""
        # Special company name mappings for better display
        display_names = {
            'company_mav': 'MÁVAG',  # Magyar Államvasutak Gépgyára
            'company_john_cockerill': 'Société anonyme John Cockerill',
            'company_ford_motor': 'Ford Motor Company',
            'company_fiat': 'FIAT',
            'company_basf': 'BASF',
            'company_us_steel': 'U.S. Steel Corporation',
            'company_general_electric': 'General Electric',
            'company_de_beers': 'De Beers Consolidated Mines Ltd.',
            'company_krupp': 'Krupp',
            'company_siemens_and_halske': 'Siemens & Halske',
            'company_standard_oil': 'Standard Oil',
            'company_united_fruit': 'United Fruit Company',
            'company_orient_express': 'Orient Express',
            'company_suez_company': 'Suez Canal Company',
            'company_east_india_company': 'British East India Company',
            'company_hbc': 'Hudson\'s Bay Company',
            'company_russian_american_company': 'Russian-American Company',
            'company_imperial_tobacco': 'Imperial Tobacco Company',
            'company_guinness': 'Guinness',
            'company_ap_moller': 'A.P. Møller',
            'company_chr_hansens': 'Chr. Hansen\'s',
            'company_philips': 'Philips',
            'company_nokia': 'Nokia',
            'company_ericsson': 'Ericsson',
            'company_lkab': 'LKAB',
            'company_norsk_hydro': 'Norsk Hydro',
            'company_skoda': 'Škoda Works',
            'company_mitsubishi': 'Mitsubishi',
            'company_mitsui': 'Mitsui & Co.',
            'company_kouppas': 'Kouppas',
            'company_basileiades': 'Basileiades',
        }
        
        # Return special name if available, otherwise format the default way
        if company_name in display_names:
            return display_names[company_name]
        
        # Remove 'company_' prefix and format
        base_name = company_name.replace('company_', '').replace('_', ' ')
        
        # Title case
        return base_name.title()

    def get_company_icon_path(self, company_name):
        """Get the icon path for a company, with comprehensive mapping"""
        # Remove company_ prefix for icon lookup
        clean_name = company_name.replace('company_', '')
        
        # Specific mappings for historical companies based on actual file names
        self.historical_mappings = {
            'us_steel': 'american_carnegie_steel',
            'carnegie_steel': 'american_carnegie_steel', 
            'ford_motor': 'american_ford',
            'general_electric': 'american_general_electric',
            'standard_oil': 'american_standard_oil',
            'united_fruit': 'american_united_fruit_co',
            'william_cramp': 'american_william_and_sons',
            'anglo_persian_oil': 'anglo_persian_oil_company',
            'ap_moller': 'ap_moller',
            'bunge_born': 'argentina_bunge_y_born',
            'centro_vitivinicola_nacional': 'argentina_centro_vitivinicola_nacional',
            'cordoba_cenral_railway': 'argentina_cordoba_cenral_railway',
            'guinness': 'arthur_guinness_son',
            'basque_altos_hornos_de_vizcaya': 'basque_altos_hornos_de_vizcaya',
            'estanifera_llallagua': 'bolivia_compania_estanifera_de_llallagua',
            'csfa': 'bolivia_csfa',
            'rossi': 'brazil_amadeo_rossi',
            'pernambuco_textiles': 'brazil_companhia_fiacai_e_tecidos_de_pernambuco',
            'estaleiro_maua': 'brazil_estaleiro_maua',
            'fundicao_ipanema': 'brazil_fundicao_ipanema',
            'kablin': 'brazil_kablin_irmaos_and_cia',
            'sao_paulo_railway': 'brazil_sao_paulo_railway',
            'ccci': 'ccci',
            'orient_express': 'chemins_de_fer_orientaux',
            'sudamericana_de_vapores': 'chile_csav',
            'famae': 'chile_fabrica_de_armas_de_la_nacion',
            'foochow_arsenal': 'chinese_foochow_arsenal',
            'hanyang_arsenal': 'chinese_hanyang_arsenal',
            'jingdezhen': 'chinese_jingdezhen_kilns',
            'kaiping_mining': 'chinese_kaiping_mining_company',
            'sansinena': 'compania_sansinena_de_carnes_congeladas',
            'aker_mek': 'company_aker_mek',
            'anglo_sicilian_sulphur_company': 'company_anglo_sicilian_sulphur_company',
            'colt_firearms': 'company_colt_firearms',
            'de_beers': 'company_de_beers',
            'gebruder_thonet': 'company_gebruder_thonet',
            'imperial_ethiopian_railways': 'company_imperial_ethiopian_railways',
            'jiangnan_weaving_bureaus': 'company_jiangnan_weaving_bureaus',
            'john_holt': 'company_john_holt',
            'kinkozan_sobei': 'company_kinkozan_sobei',
            'konigliche_porzellan_manufaktur_meissen': 'company_konigliche_porzellan_manufaktur_meissen',
            'lanfang_kongsi': 'company_lanfang_kongsi',
            'lee_wilson': 'company_lee_wilson',
            'ludwig_moser_and_sons': 'company_ludwig_moser_and_sons',
            'maison_worth': 'company_maison_worth',
            'mantero_seta': 'company_mantero_seta',
            'maple_and_co': 'company_maple_and_co',
            'massey_harris': 'company_massey_harris',
            'norsk_hydro': 'company_norsk_hydro',
            'ong_lung_sheng_tea_company': 'company_ong_lung_sheng_tea_company',
            'paradox': 'company_paradox',
            'russian_american_company': 'company_russian_american_company',
            # Additional missing mappings based on available icons
            'cfr': 'romania_cfr',
            'caile_ferate_romane': 'romania_cfr',
            'ferrocarril_central_cordoba': 'argentina_cordoba_cenral_railway',
            'great_indian_railway': 'india_great_indian_peninsula_railway',
            'great_western_railway': 'gb_great_western_railway',
            'iranian_state_railway': 'trans_iranian_railway',
            'mantetsu': 'japanese_mantetsu',
            'preussische_staatseisenbahnen': 'german_kpev',
            'new_russia_company': 'russian_new_russia_company',
            'schichau': 'german_schichau',
            'schneider': 'france_schneider_et_cie',
            'schneider_et_cie': 'france_schneider_et_cie',
            'siemens': 'german_siemens_halske',
            'siemens_halske': 'german_siemens_halske',
            'siemens_and_halske': 'german_siemens_halske',
            'west_ural_petroleum': 'historical_west_ural_petroleum_company_limited',
            'san_miguel': 'manila_la_fabrica_de_cerveza_san_miguel',
            'vodka_monopoly': 'russian_vodka_monopoly',
            'basf': 'german_basf',
            'chr_hansens': 'denmark_chr_hansens_teknisk_kemiske_laboratorium',
            'dollfus_mieg': 'france_dmc',
            'east_india_company': 'gb_eic',
            'egyptian_rail': 'egyptian_rail',
            'tata': 'india_tata',
            'mavag': 'mavag',
            'mav': 'mavag',
            'john_brown': 'gb_jb_co',
            'kirgizian_mining': 'company_john_holt',  # Placeholder for now
            'krupp': 'german_krupp',
            'la_rosada': 'paraguay_la_rosada',
            'compagnie_des_mines_anzin': 'france_compagnie_des_mines_danzin',
            'mitsubishi': 'japanese_mitsubishi',
            'mitsui': 'japanese_mitsui',
            'rheinmetall': 'german_rheinmetall',
            'saint_etienne': 'france_saint_etienne',
            'trubia': 'spain_fabrica_de_armas_de_trubia',
            'b_grimm': 'thailand_b_grimm',
            'moscow_irrigation': 'historical_moscow_irrigation_company',
            'companhia_de_mocambique': 'mozambique_companhia_de_mocambique',
            'steaua_romana': 'romania_steaua_romana',
            'persian_oil': 'historical_perskhlopok',
            'cockerill': 'john_cockerill',
            'sociedade_anonyme_john_cockerill': 'john_cockerill',
            'nam_dinh_textile': 'vietnam_nam_dinh',
            'suez_company': 'suez_company',
            'turkish_petroleum': 'turkish_petroleum_company',
            'electricidad_de_caracas': 'venezuela_c_a_la_electricidad_de_caracas',
            'caribbean_petroleum': 'venezuela_caribbean_petroleum_company',
            'william_sandford': 'william_sandford_limited',
            'zastava': 'zastava',
            'altos_hornos_de_vizcaya': 'basque_altos_hornos_de_vizcaya',
            'duro_y_compania': 'spain_duro_y_compania',
            'lilpop': 'polish_lilpop',
            'societe_mokta_el_hadid': 'france_société_mokta_el_hadid',
            'bengal_coal': 'ip2_bengal_coal_company',
            'bolckow_vaughan': 'gb_bolckow_vaughan_and_co',
            'bombay_burmah_trading': 'ip2_bombay_burmah_trading',
            'peruvian_amazon': 'peru_peruvian_amazon_company',
            'madura_mills': 'ip2_madura_mills',
            'steel_brothers': 'ip2_steel_brothers_and_co',
            'ericsson': 'ericsson',
            'lkab': 'lkab',
            'gotaverken': 'götaverken',
            'afghanistan_national_weaving': 'da_afghan_nassaji_sherkat',
            'national_iranian_oil': 'national_iranian_oil_company',
            'tashkent_railroad': 'tashkent_railroad',
            'tersane_i_amire': 'imperial_arsenal',
            'ottoman_tobacco_regie': 'ottoman_tobacco_regie',
            # Fix remaining exact company ID matches
            'prussian_state_railways': 'german_kpev',
            'armstrong_whitworth': 'gb_armstrong_whitworth',
            'john_brown': 'gb_jb_co',
            'schneider_creusot': 'france_schneider_et_cie',
            'john_cockerill': 'john_cockerill',
            # More exact company name fixes
            'gwr': 'gb_great_western_railway',
            'wadia_shipbuilders': 'ip2_wadia_shipbuilders',
            'ralli_brothers': 'ip2_ralli_brothers',
            'putilov_company': 'russian_putilov',
            'fcm': 'france_forges_et_chantiers_de_la_méditerranée',
            'mines_anzin': 'france_compagnie_des_mines_danzin',
            'j_p_coats': 'gb_jp_coats',
            # Additional missing mappings identified by user
            'sunhwaguk': 'korea_sunhwaguk',
            'dmc': 'france_dmc',
            'nokia': 'finland_nokia',
            'ericsson': 'ericsson',
            'branobel': 'russian_branobel',
            'izhevsk_arms_plant': 'russian_izhevsk_arms_plant',
            # Newly found icon mappings
            'ursus': 'polish_ursus',
            'cordoba_railway': 'argentina_cordoba_cenral_railway',
            'john_hughes': 'russian_new_russia_company',
            'david_sassoon': 'ip2_david_sasson_and_co',
            'bombay_dyeing_company': 'ip2_bombay_dyeing',
            'nam_dinh': 'vietnam_nam_dinh',
            'savva_morozov': 'russian_savva_morozov_and_sons',
            'sherkate_eslamiya': 'historical_serkat_e_eslamiya',
            'perskhlopok': 'historical_perskhlopok',
            'persshelk': 'historical_persshelk',
            'cgv': 'france_cgv',
            'maatschappij': 'maatschappij',
            'steaua_romana': 'romania_steaua_romana',
            # Systematic matches from available icons
            'bengal_coal_company': 'ip2_bengal_coal_company',
            'bombay_burmah_trading_corporation': 'ip2_bombay_burmah_trading',
            'assam_company': 'ip2_assam_company',
            'calcutta_electric': 'ip2_calcutta_electric',
            'mozambique_company': 'mozambique_companhia_de_mocambique',
            'espana_industrial': 'spain_la_espana_industrial',
            'argentinian_wine': 'argentina_centro_vitivinicola_nacional',
            'eea': 'peru_empresas_electricas_asociadas',
            'nicolas_portalis': 'historical_mm_nicolas_portalis_et_cie',
            'moscow_irrigation_company': 'historical_moscow_irrigation_company',
            'peruvian_amazon': 'peru_peruvian_amazon_company'
        }
        
        # Check historical mappings first
        if clean_name in self.historical_mappings:
            historical_path = "companies/png/historical_company_icons/{}.png".format(self.historical_mappings[clean_name])
            full_path = os.path.join(os.path.dirname(__file__), historical_path)
            if os.path.exists(full_path):
                return historical_path
        
        # Try different icon paths in order of preference
        icon_candidates = [
            # Direct historical company icons match
            "companies/png/historical_company_icons/{}.png".format(clean_name),
            
            # Basic company types with exact name match
            "companies/png/{}.png".format(clean_name),
            "companies/png/company_{}.png".format(clean_name),
            "companies/png/basic_{}.png".format(clean_name),
            
            # Try some common transformations for basic companies
            "companies/png/basic_{}.png".format(clean_name.split('_')[-1]) if '_' in clean_name else None,
        ]
        
        # Filter out None values
        icon_candidates = [c for c in icon_candidates if c is not None]
        
        # Return the first existing icon path
        for candidate in icon_candidates:
            full_path = os.path.join(os.path.dirname(__file__), candidate)
            if os.path.exists(full_path):
                return candidate
        
        # Debug: print missing company icon
        print("WARNING: Missing company icon for: {} (clean: {})".format(company_name, clean_name))
        
        # If no icon found, return placeholder
        return "companies/png/custom_companies_placeholder.png"
    
    def setup_company_icon_mapping(self):
        """Setup mapping of company names to their icon files"""
        self.company_icons = {}
        companies_dir = os.path.join(os.path.dirname(__file__), "companies")
        
        if not os.path.exists(companies_dir):
            return
        
        # Scan for available icon files
        for root, dirs, files in os.walk(companies_dir):
            for file in files:
                if file.endswith(('.dds', '.png')):
                    # Extract company name from filename
                    base_name = file.replace('.dds', '').replace('.png', '')
                    company_key = "company_{}".format(base_name)
                    
                    # Store the relative path
                    rel_path = os.path.relpath(os.path.join(root, file), os.path.dirname(__file__))
                    self.company_icons[company_key] = rel_path
                    
    def infer_country_from_filename(self, filename):
        """Infer country from company file name"""
        filename_to_country = {
            '00_companies_usa.txt': 'USA',
            '00_companies_great_britain.txt': 'GBR', 
            '00_companies_france.txt': 'FRA',
            '00_companies_germany.txt': 'DEU',
            '00_companies_russia.txt': 'RUS',
            '00_companies_austria_hungary.txt': 'AUS',
            '00_companies_italy.txt': 'ITA',
            '00_companies_china.txt': 'CHI',
            '00_companies_japan.txt': 'JAP',
            '00_companies_asia.txt': None,  # Mixed countries
            '00_companies_africa.txt': None,  # Mixed countries
            '00_companies_americas.txt': None,  # Mixed countries
            '00_companies_europe.txt': None,  # Mixed countries
        }
        return filename_to_country.get(filename, None)
    
    def get_company_country_override(self, company_name):
        """Manual country assignments for companies without state requirements"""
        company_countries = {
            # Argentine companies
            'company_argentinian_wine': 'ARG',  # Centro Vitivinícola Nacional (Argentina)
            
            # Russian companies (from icon/name analysis)
            'company_perskhlopok': 'RUS',  # Russian cotton company
            'company_persshelk': 'RUS',    # Russian silk company
            
            # Brazilian companies
            'company_kablin': 'BRZ',       # Kablin Irmãos & Cia (Brazil)
            
            # British companies
            'company_john_holt': 'GBR',    # John Holt & Co (British trading)
            'company_imperial_tobacco': 'GBR',  # Imperial Tobacco
            'company_east_india_company': 'GBR', # East India Company
            
            # Iranian companies  
            'company_iranian_state_railway': 'PER',  # Iran
            
            # Korean companies
            'company_sunhwaguk': 'KOR',    # Korean company
            
            # South African companies
            'company_de_beers': 'SAF',     # De Beers (South Africa)
            
            # Myanmar/British Burma
            'company_steel_brothers': 'BUR', # Steel Brothers & Co
            
            # Romanian companies
            'company_cfr': 'ROM',          # Romanian railways
            
            # Philippines companies  
            'company_san_miguel': 'PHI',   # San Miguel (Philippines)
            
            # Indian companies
            'company_great_indian_railway': 'IND', # Great Indian Peninsula Railway
            
            # Mexican companies
            'company_el_aguila': 'MEX',    # El Águila (Mexico)
            
            # Egyptian companies
            'company_egyptian_rail': 'EGY', # Egyptian railways
            
            # Chinese companies
            'company_ong_lung_sheng_tea_company': 'CHI', # Chinese tea company
            
            # Ottoman companies
            'company_ottoman_tobacco_regie': 'TUR', # Ottoman Tobacco
            
            # Ethiopian companies
            'company_imperial_ethiopian_railways': 'ETH', # Ethiopian railways
            
            # Argentine companies
            'company_bunge_born': 'ARG',   # Bunge & Born (Argentina)
            
            # Dutch companies
            'company_nederlandse_petroleum': 'NET', # Nederlandse Petroleum
            
            # US/Russian Alaska company
            'company_russian_american_company': 'RUS', # Russian-American Company
            
            # French railways
            'company_orient_express': 'FRA', # Orient Express
            
            # Chinese opium
            'company_opium_export_monopoly': 'CHI', # Chinese opium monopoly
            
            # Development companies - based on formation requirements
            'company_oriental_development_company': 'KOR', # Requires Korean homeland states
            'company_ccci': 'BEL',         # Compagnie du Congo (Belgian colonial company)
            'company_paradox': 'SWE',      # Paradox is Swedish ;)
        }
        return company_countries.get(company_name, None)

    def setup_prestige_good_names(self):
        """Map prestige good codes to display names"""
        self.prestige_good_names = {
            'prestige_good_generic_grain': 'Fine Grain',
            'prestige_good_generic_meat': 'Prime Meat', 
            'prestige_good_generic_coffee': 'Reserve Coffee',
            'prestige_good_generic_opium': 'Pure Opium',
            'prestige_good_generic_fish': 'Select Fish',
            'prestige_good_generic_groceries': 'Gourmet Groceries',
            'prestige_good_generic_paper': 'Craft Paper',
            'prestige_good_generic_furniture': 'Stylish Furniture',
            'prestige_good_generic_clothes': 'Designer Clothes',
            'prestige_good_generic_steel': 'Refined Steel',
            'prestige_good_generic_tools': 'Precision Tools',
            'prestige_good_generic_fertilizer': 'Enriched Fertilizer',
            'prestige_good_generic_explosives': 'High Grade Explosives',
            'prestige_good_generic_small_arms': 'High Powered Small Arms',
            'prestige_good_generic_artillery': 'Quick Fire Artillery',
            'prestige_good_generic_merchant_marine': 'Swift Merchant Marine'
        }
        
    def get_building_icon_path(self, building_name):
        """Get the icon path for a building, flagging missing building icons"""
        # Building name mappings for icon files that have different names
        building_name_mappings = {
            'building_chemical_plants': 'chemicals_industry',
            'building_textile_mills': 'textile_industry', 
            'building_artillery_foundries': 'artillery_foundry',
            'building_automotive_industry': 'vehicles_industry',
            'building_livestock_ranch': 'cattle_ranch',
            'building_rubber_plantation': 'rubber_lodge',
            'building_vineyard_plantation': 'vineyards'
        }
        
        # Check if we have a mapping for this building name
        if building_name in building_name_mappings:
            mapped_name = building_name_mappings[building_name]
            building_icon_64px = "buildings/64px-Building_{}.png".format(mapped_name)
            full_building_path_64px = os.path.join(os.path.dirname(__file__), building_icon_64px)
            
            if os.path.exists(full_building_path_64px):
                return building_icon_64px
        
        # Priority 1: Try 64px building icon format (the actual format in buildings folder)
        clean_building_name = building_name.replace('building_', '')
        building_icon_64px = "buildings/64px-Building_{}.png".format(clean_building_name)
        full_building_path_64px = os.path.join(os.path.dirname(__file__), building_icon_64px)
        
        if os.path.exists(full_building_path_64px):
            return building_icon_64px
        
        # Priority 2: Try exact building name
        building_icon_path = "buildings/{}.png".format(building_name)
        full_building_path = os.path.join(os.path.dirname(__file__), building_icon_path)
        
        if os.path.exists(full_building_path):
            return building_icon_path
        
        # Priority 3: Try clean building name
        building_icon_path_clean = "buildings/{}.png".format(clean_building_name)
        full_building_path_clean = os.path.join(os.path.dirname(__file__), building_icon_path_clean)
        
        if os.path.exists(full_building_path_clean):
            return building_icon_path_clean
        
        # Flag missing building icon
        if not hasattr(self, 'missing_building_icons'):
            self.missing_building_icons = set()
        self.missing_building_icons.add(building_name)
        print("WARNING: Missing building icon: {} (tried: {})".format(building_name, building_icon_64px))
        
        # Return None to indicate missing icon
        return None
    
    def abbreviate_company_name(self, display_name, max_length=35):
        """Abbreviate company name if it's too long, preserving meaning"""
        if len(display_name) <= max_length:
            return display_name
        
        # Common abbreviations
        abbreviations = {
            'Company': 'Co.',
            'Corporation': 'Corp.',
            'Limited': 'Ltd.',
            'Manufacturing': 'Mfg.',
            'Incorporated': 'Inc.',
            'International': 'Intl.',
            'Development': 'Dev.',
            'Industries': 'Ind.',
            'Association': 'Assoc.',
            'Gesellschaft': 'GmbH',
            'Aktiengesellschaft': 'AG',
            'and': '&',
            'Railway': 'RR',
            'Railroad': 'RR',
            'Petroleum': 'Oil',
            'Electric': 'Elec.',
            'Telephone': 'Tel.',
        }
        
        # Apply abbreviations
        abbreviated = display_name
        for full, abbrev in abbreviations.items():
            abbreviated = abbreviated.replace(full, abbrev)
        
        # If still too long, truncate intelligently
        if len(abbreviated) > max_length:
            # Try to keep the main company name (before comma or dash)
            if ',' in abbreviated:
                main_part = abbreviated.split(',')[0].strip()
                if len(main_part) <= max_length - 3:
                    return main_part + '...'
            
            if ' - ' in abbreviated:
                main_part = abbreviated.split(' - ')[0].strip()
                if len(main_part) <= max_length - 3:
                    return main_part + '...'
            
            # Last resort: truncate with ellipsis
            return abbreviated[:max_length-3] + '...'
        
        return abbreviated
    
    def get_company_building_stats(self, company_name):
        """Get building counts and prestige goods for a company"""
        if company_name not in self.companies:
            return 0, 0, []
        
        data = self.companies[company_name]
        base_count = len(data.get('building_types', []))
        charter_count = len(data.get('extension_building_types', []))
        prestige_goods = []
        
        # Check for prestige goods across all buildings
        all_buildings = set(data.get('building_types', []) + data.get('extension_building_types', []))
        for building in all_buildings:
            has_prestige_result = self.company_has_prestige_for_building(company_name, building)
            if isinstance(has_prestige_result, tuple):
                has_prestige, prestige_good = has_prestige_result
                if has_prestige and prestige_good and prestige_good not in prestige_goods:
                    prestige_goods.append(prestige_good)
            elif has_prestige_result:
                # If it's just a boolean True, we know there's prestige but not which good
                # We'll handle this case by looking for any prestige goods in the company data
                if hasattr(data, 'prestige_goods') and data.prestige_goods:
                    for pg in data.prestige_goods:
                        if pg not in prestige_goods:
                            prestige_goods.append(pg)
        
        return base_count, charter_count, prestige_goods
    
    def format_building_count(self, base_count, charter_count):
        """Format building count as decimal notation (e.g., 3.2 for 3 base, 2 charter)"""
        if charter_count > 0:
            return "{}.{}".format(base_count, charter_count)
        else:
            return str(base_count)
    
    def get_company_prestige_icons(self, company_name):
        """Get prestige icons HTML for a company"""
        if company_name not in self.companies:
            return ''
        
        data = self.companies[company_name]
        prestige_icons_html = ''
        prestige_goods = []
        
        # Check for prestige goods across all buildings
        all_buildings = set(data.get('building_types', []) + data.get('extension_building_types', []))
        for building in all_buildings:
            has_prestige_result = self.company_has_prestige_for_building(company_name, building)
            if isinstance(has_prestige_result, tuple):
                has_prestige, prestige_good = has_prestige_result
                if has_prestige and prestige_good and prestige_good not in prestige_goods:
                    prestige_goods.append(prestige_good)
            elif has_prestige_result:
                # If it's just a boolean True, we know there's prestige but not which good
                if hasattr(data, 'prestige_goods') and data.prestige_goods:
                    for pg in data.prestige_goods:
                        if pg not in prestige_goods:
                            prestige_goods.append(pg)
        
        # Generate prestige icons HTML
        for prestige_good in prestige_goods:
            prestige_good_base = prestige_good.replace('prestige_good_generic_', '').replace('prestige_good_', '')
            
            # Special icon mappings for prestige goods that don't have exact icon matches
            icon_mappings = {
                'burmese_teak': 'teak',
                'swedish_bar_iron': 'oregrounds_iron'
            }
            
            if prestige_good_base in icon_mappings:
                prestige_good_base = icon_mappings[prestige_good_base]
            
            # Try prestige-specific icon first, fallback to goods icon
            prestige_icon_24px = "icons/24px-Prestige_{}.png".format(prestige_good_base)
            prestige_icon_40px = "icons/40px-Goods_{}.png".format(prestige_good_base)
            
            icon_path = None
            if os.path.exists(prestige_icon_24px):
                icon_path = prestige_icon_24px
            elif os.path.exists(prestige_icon_40px):
                icon_path = prestige_icon_40px
            
            if icon_path:
                prestige_icons_html += '<img src="{}" class="prestige-icon" alt="{}" title="{}">'.format(
                    icon_path, prestige_good_base.title(), prestige_good_base.replace('_', ' ').title()
                )
        
        return prestige_icons_html

    def parse_state_to_country_mappings(self):
        """Parse state to country mappings from game files"""
        try:
            import codecs
            with codecs.open(self.states_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all state definitions with country assignments
            state_pattern = r's:(\w+)\s*=\s*\{[^{}]*?create_state\s*=\s*\{[^{}]*?country\s*=\s*c:(\w+)'
            matches = re.findall(state_pattern, content)
            
            for state, country in matches:
                self.state_to_country[state] = country
                
            print("Parsed {} state-to-country mappings".format(len(self.state_to_country)))
        except Exception as e:
            print("Error parsing state mappings: {}".format(e))

    def parse_subject_relationships(self):
        """Parse subject relationships from diplomacy files"""
        try:
            import codecs
            with codecs.open(self.diplomacy_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find diplomatic pacts with subject relationships
            # Pattern: country = c:SUBJECT followed by type = (protectorate|puppet|tributary|personal_union|dominion|colony|chartered_company)
            pact_pattern = r'c:(\w+)\s*\?\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
            overlord_matches = re.findall(pact_pattern, content)
            
            subject_types = {'protectorate', 'puppet', 'tributary', 'personal_union', 'dominion', 'colony', 'chartered_company'}
            
            for overlord, pacts_content in overlord_matches:
                # Find individual diplomatic pacts within this overlord's section
                pact_detail_pattern = r'create_diplomatic_pact\s*=\s*\{([^{}]+)\}'
                pact_details = re.findall(pact_detail_pattern, pacts_content)
                
                for pact_detail in pact_details:
                    # Extract country and type from the pact
                    country_match = re.search(r'country\s*=\s*c:(\w+)', pact_detail)
                    type_match = re.search(r'type\s*=\s*(\w+)', pact_detail)
                    
                    if country_match and type_match:
                        subject = country_match.group(1)
                        relationship_type = type_match.group(1)
                        
                        if relationship_type in subject_types:
                            self.subject_relationships[subject] = overlord
                            
            # Add manual overrides for historical accuracy (as mentioned by user)
            manual_overrides = {
                'LAN': 'CHI',  # Lanfang subject to Great Qing
                'LUX': 'BEL',  # Luxembourg subject to Belgium (later in timeline)
                # Add more as needed
            }
            
            self.subject_relationships.update(manual_overrides)
                            
            print("Parsed {} subject relationships".format(len(self.subject_relationships)))
            for subject, overlord in self.subject_relationships.items():
                print("  {} is subject to {}".format(subject, overlord))
                
        except Exception as e:
            print("Error parsing subject relationships: {}".format(e))

    def get_effective_country(self, country):
        """Get the effective country for company formation, considering subject relationships if enabled"""
        if self.use_subject_relationships:
            return self.subject_relationships.get(country, country)
        return country

    def parse_wiki_data(self):
        """Parse wiki data for company-country associations"""
        if not os.path.exists(self.wiki_file):
            print("Wiki file not found, skipping cross-check")
            return
            
        try:
            import codecs
            with codecs.open(self.wiki_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse wiki format: Country sections (===Country===) with company tables
            current_country = None
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Look for country headers: ===Country===
                if line.startswith('===') and line.endswith('==='):
                    current_country = line.strip('= ')
                    continue
                
                # Look for table rows starting with | that contain company names
                if line.startswith('|') and current_country and not line.startswith('|-') and not line.startswith('!'):
                    # Extract company name from wiki table row
                    # Company names can be in formats like:
                    # | Company Name
                    # | {{icon|cotsb}} Company Name  
                    # | [[Company Name]]
                    
                    company_line = line[1:].strip()  # Remove leading |
                    
                    # Skip empty lines, building lists, requirement lists, etc.
                    if not company_line or company_line.startswith('*') or company_line.startswith('{{iconify') or company_line.startswith('{{green') or company_line.startswith('{{red'):
                        continue
                    
                    # Extract company name from various wiki formats
                    company_name = self.extract_company_name_from_wiki_line(company_line)
                    
                    if company_name:
                        # Store both raw name and normalized versions for matching
                        wiki_key = self.normalize_company_name(company_name)
                        if wiki_key:  # Only store if we get a valid normalized name
                            self.wiki_companies[wiki_key] = current_country
                    
            print("Parsed {} company-country associations from wiki".format(len(self.wiki_companies)))
            if len(self.wiki_companies) > 0:
                print("Sample wiki companies:")
                for i, (company, country) in enumerate(self.wiki_companies.items()):
                    if i < 5:  # Show first 5
                        print("  {} -> {}".format(company, country))
                    
        except Exception as e:
            print("Error parsing wiki data: {}".format(e))
    
    def extract_company_name_from_wiki_line(self, line):
        """Extract company name from a wiki table line"""
        # Remove wiki markup
        import re
        
        # Remove {{icon|cotsb}} and similar
        line = re.sub(r'\{\{icon\|[^}]+\}\}', '', line)
        
        # Remove links [[Company Name]] -> Company Name
        line = re.sub(r'\[\[([^\]]+)\]\]', r'\1', line)
        
        # Remove other template markup
        line = re.sub(r'\{\{[^}]+\}\}', '', line)
        
        # Clean up whitespace
        line = line.strip()
        
        # Skip lines that are clearly not company names
        if not line or line.startswith('*') or line.startswith('{{') or len(line) < 3:
            return None
            
        # Take first part before any additional content (like building lists)
        if '|' in line:
            line = line.split('|')[0].strip()
            
        return line
    
    def normalize_company_name(self, wiki_name):
        """Normalize wiki company name to match with extracted company names"""
        if not wiki_name:
            return None
            
        # Convert to lowercase and replace spaces/hyphens with underscores
        normalized = wiki_name.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        normalized = re.sub(r'\s+', '_', normalized)  # Spaces to underscores
        normalized = normalized.replace('-', '_')
        
        # Add company_ prefix to match extracted format
        if not normalized.startswith('company_'):
            normalized = 'company_' + normalized
            
        return normalized if len(normalized) > 8 else None  # Must have actual content after company_

    def map_wiki_country_to_code(self, wiki_country):
        """Map wiki country names to game country codes"""
        # Wiki country name to game code mapping
        country_mapping = {
            # Major countries
            'Argentina': 'ARG',
            'Australia': 'AST', 
            'Austria-Hungary': 'AUS',
            'Belgium': 'BEL',
            'Brazil': 'BRZ',
            'Canada': 'CAN',
            'Chile': 'CHL',
            'China': 'CHI',
            'Colombia': 'CLM',
            'Denmark': 'DEN',
            'Egypt': 'EGY',
            'Ethiopia': 'ETH',
            'France': 'FRA',
            'Germany': 'DEU',
            'Great Britain': 'GBR',
            'Greece': 'GRE',
            'India': 'BIC',  # British East India Company
            'Italy': 'ITA',
            'Japan': 'JAP',
            'Korea': 'KOR',
            'Mexico': 'MEX',
            'Netherlands': 'NET',
            'Niger': 'SOK',  # Sokoto Caliphate
            'Norway': 'NOR',
            'Paraguay': 'PRG',
            'Persia': 'PER',
            'Peru': 'PEU',
            'Poland': 'POL',
            'Portugal': 'POR',
            'Russia': 'RUS',
            'Serbia': 'SER',
            'Spain': 'SPA',
            'Sweden': 'SWE',
            'Turkey': 'TUR',
            'Turkestan': 'KOK',  # Kokand
            'United States': 'USA',
            'Venezuela': 'VNZ',
            
            # Additional mappings as needed
            'Ottoman Empire': 'TUR',
            'Qing': 'CHI',
            'Siam': 'SIA',
            'Two Sicilies': 'SIC',
            'Sardinia-Piedmont': 'SAR',
            'Prussia': 'PRU',
            'Bavaria': 'BAV',
            'Saxony': 'SAX',
            'Baden': 'BAD',
            'Hanover': 'HAN',
            'Wurttemberg': 'WUR',
        }
        
        return country_mapping.get(wiki_country, None)

    def find_wiki_country_for_company(self, company_name):
        """Find wiki country for a company using direct match or aliases"""
        # First try direct match
        if company_name in self.wiki_companies:
            wiki_country = self.wiki_companies[company_name]
            return self.map_wiki_country_to_code(wiki_country)
        
        # Manual aliases for common mismatches between wiki formal names and game internal names
        company_aliases = {
            # Format: 'game_internal_name': 'wiki_country_code'
            'company_john_cockerill': 'BEL',  # Société anonyme John Cockerill
            'company_franco_belge': 'BEL',    # Société Franco-Belge
            'company_krupp': 'DEU',           # Friedrich Krupp
            'company_rheinmetall': 'DEU',     # Rheinmetall
            'company_schichau': 'DEU',        # F. Schichau
            'company_siemens_and_halske': 'DEU', # Siemens & Halske
            'company_basf': 'DEU',            # BASF
            'company_konigliche_porzellan_manufaktur_meissen': 'DEU', # Königliche Porzellan-Manufaktur Meissen
            'company_j_p_coats': 'GBR',       # J. P. Coats
            'company_armstrong_whitworth': 'GBR', # Sir W. G. Armstrong Whitworth & Co.
            'company_john_brown': 'GBR',      # John Brown Company
            'company_gwr': 'GBR',            # Great Western Railway
            'company_bolckow_vaughan': 'GBR', # Bolckow, Vaughan & Co.
            'company_guinness': 'GBR',       # Arthur Guinness Son & Co. Ltd.
            'company_maple_and_co': 'GBR',   # Maple & Co.
            'company_hbc': 'CAN',            # Hudson's Bay Company
            'company_massey_harris': 'CAN',   # Massey-Harris Limited
            'company_standard_oil': 'USA',   # Standard Oil
            'company_us_steel': 'USA',       # Carnegie Steel Co.
            'company_general_electric': 'USA', # General Electric
            'company_william_cramp': 'USA',  # William Cramp & Sons
            'company_ford_motor': 'USA',     # Ford Motor Company
            'company_colt_firearms': 'USA',  # Colt's Patent Firearms Manufacturing Company
            'company_lee_wilson': 'USA',     # Lee Wilson Company
            'company_united_fruit': 'USA',   # United Fruit Company
            'company_bunge_born': 'ARG',     # Bunge & Born
            'company_compania_sansinena_de_carnes_congeladas': 'ARG', # Compañía Sansinena de Carnes Congeladas
            'company_csfa': 'BOL',           # Compañía de Salitres y Ferrocarril de Antofagasta
            'company_estanifera_llallagua': 'BOL', # Compañía Estañífera de Llallagua
            'company_sao_paulo_railway': 'BRZ', # São Paulo Railway Co. Ltd
            'company_estaleiro_maua': 'BRZ', # Estaleiro Mauá
            'company_pernambuco_textiles': 'BRZ', # Companhia Fiação e Tecidos de Pernambuco
            'company_fundicao_ipanema': 'BRZ', # Fundição Ipanema
            'company_rossi': 'BRZ',          # Amadeo Rossi & Cia
            'company_kablin': 'BRZ',         # Klabin Irmãos & Cia
            'company_fundidora_monterrey': 'MEX', # Fundidora de Fierro y Acero de Monterrey
            'company_el_aguila': 'MEX',      # El Águila
            'company_famae': 'CHL',          # Fábrica de Armas de la Nación
            'company_sudamericana_de_vapores': 'CHL', # Compañía Sudamericana de Vapores
            'company_la_rosada': 'PRG',      # La Rosada
            'company_peruvian_amazon': 'PEU', # Peruvian Amazon Company
            'company_eea': 'PEU',            # Empresas Eléctricas Asociadas
            'company_caribbean_petroleum': 'VNZ', # Caribbean Petroleum Company
            'company_electricidad_de_caracas': 'VNZ', # C.A. La Electricidad de Caracas
            'company_panama_company': 'CLM', # Panama Canal Company
            'company_william_sandford': 'AST', # William Sandford Limited
            'company_kaiping_mining': 'CHI', # Kaiping Mining Company
            'company_hanyang_arsenal': 'CHI', # Hanyang Arsenal
            'company_foochow_arsenal': 'CHI', # Foochow Shipyards
            'company_jingdezhen': 'CHI',     # Jingdezhen Kilns
            'company_jiangnan_weaving_bureaus': 'CHI', # Jiangnan Weaving Bureaus
            'company_ong_lung_sheng_tea_company': 'CHI', # Ong Lung Sheng Tea Company
            'company_assam_company': 'BIC',  # Assam Company
            'company_bengal_coal_company': 'BIC', # Bengal Coal Company
            'company_bombay_burmah_trading_corporation': 'BIC', # Bombay Burmah Trading Corporation
            'company_bombay_dyeing_company': 'BIC', # Bombay Dyeing and Manufacturing Company Limited
            'company_calcutta_electric': 'BIC', # Calcutta Electric Supply Corporation Limited
            'company_david_sassoon': 'BIC',  # David Sassoon & Co. Ltd
            'company_east_india_company': 'BIC', # East India Company
            'company_great_indian_railway': 'BIC', # Great Indian Peninsula Railway
            'company_madura_mills': 'BIC',   # Madura Mills Co. Ltd
            'company_ralli_brothers': 'BIC', # Ralli Brothers
            'company_steel_brothers': 'BIC', # Steel Brothers & Co. Ltd
            'company_tata': 'BIC',           # Tata
            'company_wadia_shipbuilders': 'BIC', # Wadia Shipbuilders
            'company_mitsui': 'JAP',         # Mitsui
            'company_mantetsu': 'JAP',       # South Manchuria Railway
            'company_mitsubishi': 'JAP',     # Mitsubishi
            'company_kinkozan_sobei': 'JAP', # Kinkozan Sobei
            'company_sunhwaguk': 'KOR',      # Sunhwaguk
            'company_hanseong_jeongi_hoesa': 'KOR', # Hanseong Jeongi Hoesa
            'company_oriental_development_company': 'KOR', # Oriental Development Company
            'company_lanfang_kongsi': 'LAN', # Lanfang Kongsi
            'company_san_miguel': 'PHI',     # San Miguel
            'company_b_grimm': 'SIA',        # B. Grimm
            'company_nam_dinh': 'DAI',       # Nam Định Textile Factory
            'company_skoda': 'AUS',          # Škoda Works
            'company_mav': 'AUS',            # MÁVAG
            'company_manfred_weiss': 'AUS',  # Manfréd Weiss Steel and Metal Works
            'company_galician_carpathian_oil': 'AUS', # Galician Carpathian Petroleum Company
            'company_oevg': 'AUS',           # Österreichische Waffenfabriksgesellschaft
            'company_ludwig_moser_and_sons': 'AUS', # Glasfabrik Ludwig Moser & Söhne
            'company_gebruder_thonet': 'AUS', # Gebrüder Thonet
            'company_compagnie_du_congo': 'BEL', # Compagnie du Congo
            'company_chr_hansens': 'DEN',    # Chr. Hansen
            'company_ap_moller': 'DEN',      # A.P. Møller
            'company_nokia': 'FIN',          # Nokia
            'company_societe_mokta_el_hadid': 'FRA', # Société Mokta El Hadid
            'company_schneider_creusot': 'FRA', # Schneider et Cie
            'company_dmc': 'FRA',            # Dollfus-Mieg et Compagnie
            'company_cgv': 'FRA',            # Confédération Générale des Vignerons
            'company_saint_etienne': 'FRA',  # Manufacture d'armes de Saint-Étienne
            'company_fcm': 'FRA',            # Forges et Chantiers de la Méditerranée
            'company_mines_anzin': 'FRA',    # Compagnie des mines d'Anzin
            'company_maison_worth': 'FRA',   # Maison Worth
            'company_basileiades': 'GRE',    # Basileiades
            'company_kouppas': 'GRE',        # Kouppas
            'company_ilva': 'ITA',           # Ilva
            'company_ansaldo': 'ITA',        # Gio. Ansaldo & C.
            'company_fiat': 'ITA',           # Fiat
            'company_ricordi': 'ITA',        # G. Ricordi & C.
            'company_stt': 'ITA',            # Stabilimento Tecnico Triestino
            'company_anglo_sicilian_sulphur_company': 'ITA', # Anglo-Sicilian Sulphur Company
            'company_mantero_seta': 'ITA',   # Mantero Seta
            'company_nederlandse_petroleum': 'NET', # Nederlandse Petroleum Maatschappij
            'company_philips': 'NET',        # Philips
            'company_aker_mek': 'NOR',       # Agers Mechaniske Værksted
            'company_norsk_hydro': 'NOR',    # Norsk Hydro-Elektrisk Kvælstofaktieselskap
            'company_ursus': 'POL',          # Ursus
            'company_lilpop': 'POL',         # Lilpop, Rau i Loewenstein
            'company_mozambique_company': 'POR', # Companhia de Moçambique
            'company_cfr': 'ROM',            # Căile Ferate Române
            'company_romanian_star': 'ROM',  # Steaua Română
            'company_vodka_monopoly': 'RUS', # Vodka Monopoly
            'company_putilov_company': 'RUS', # Society of Putilov Factories
            'company_branobel': 'RUS',       # Branobel
            'company_izhevsk_arms_plant': 'RUS', # Izhevsk Arms Plant
            'company_savva_morozov': 'RUS',  # Savva Morozov & Sons
            'company_john_hughes': 'RUS',    # New Russia Company Ltd
            'company_russian_american_company': 'RUS', # Russian-American Company
            'company_zastava': 'SER',        # Zastava
            'company_altos_hornos_de_vizcaya': 'SPA', # Altos Hornos de Vizcaya
            'company_duro_y_compania': 'SPA', # Duro y Compañía
            'company_espana_industrial': 'SPA', # La España Industrial
            'company_trubia': 'SPA',         # Fábrica de Armas de Trubia
            'company_ericsson': 'SWE',       # Ericsson
            'company_lkab': 'SWE',           # LKAB
            'company_gotaverken': 'SWE',     # Götaverken
            'company_paradox': 'SWE',        # John Paradox Company
            'company_da_afghan_nassaji_sherkat': 'AFG', # Də Afḡān Nasājī Šerkat
            'company_sherkat_shemali': 'AFG', # Šerkate Etteḥādīyaye Welāyate Šemālī
            'company_misr': 'EGY',           # Misr Spinning and Weaving Company
            'company_egyptian_rail': 'EGY',  # Egyptian State Railways
            'company_suez_company': 'EGY',   # Suez Canal Company
            'company_nicolas_portalis': 'EGY', # MM. Nicolas Portalis et Cie
            'company_imperial_tobacco': 'PER', # Imperial Tobacco Corporation of Persia
            'company_iranian_state_railway': 'PER', # Iranian State Railway
            'company_opium_export_monopoly': 'PER', # Bongāhe Enḥeṣāre Ṣāderāte Taryāk
            'company_sherkate_eslamiya': 'PER', # Šerkate Eslāmiya
            'company_persshelk': 'PER',      # Persshelk
            'company_perskhlopok': 'PER',    # Perskhlopok
            'company_moscow_irrigation_company': 'PER', # Moscow Irrigation Company
            'company_anglo_persian_oil': 'PER', # Anglo-Persian Oil Company
            'company_national_iranian_oil': 'PER', # National Iranian Oil Company
            'company_tashkent_railroad': 'KOK', # Tashkent Railroad
            'company_west_ural_petroleum': 'KOK', # West Ural Petroleum Company Limited
            'company_kirgizian_mining_company': 'KOK', # Kirgizian Mining Joint Stock Company
            'company_imperial_arsenal': 'TUR', # Tersânei Âmire
            'company_ottoman_tobacco_regie': 'TUR', # Ottoman Tobacco Company
            'company_allatini_mills': 'TUR',  # Allatini Mills
            'company_orient_express': 'TUR',  # Chemins de Fer Orientaux
            'company_turkish_petroleum': 'TUR', # Turkish Petroleum Company
            'company_imperial_ethiopian_railways': 'ETH', # Imperial Ethiopian Railway Company
            'company_john_holt': 'SOK',       # John Holt and Company (Niger)
            'company_de_beers': 'SAF',        # De Beers Consolidated Mines Ltd
            'company_prussian_state_railways': 'DEU', # Preußische Staatseisenbahnen (file_based -> wiki)
            'company_ccci': 'BEL',            # Compagnie du Congo -> wiki assignment (Belgium)
        }
        
        return company_aliases.get(company_name, None)

    def parse_prestige_goods(self):
        """Parse prestige goods to map them to their base goods"""
        try:
            import codecs
            with codecs.open(self.prestige_goods_dir, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find prestige good definitions
            prestige_pattern = r'(prestige_good_\w+)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
            prestige_matches = re.findall(prestige_pattern, content)
            
            for prestige_good, prestige_content in prestige_matches:
                # Look for base_good definition
                base_good_match = re.search(r'base_good\s*=\s*(\w+)', prestige_content)
                if base_good_match:
                    base_good = base_good_match.group(1)
                    self.prestige_goods[prestige_good] = base_good
                    
            print("Parsed {} prestige goods mappings".format(len(self.prestige_goods)))
        except Exception as e:
            print("Error parsing prestige goods: {}".format(e))

    def parse_paradox_file(self, content):
        """Parse Paradox script format files"""
        # Remove BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]
            
        companies = {}
        
        # Find all company definitions WITH their preceding comments - before removing comments
        company_pattern = r'(?:#\s*([^\n]*)\n\s*)?(company_\w+)\s*=\s*\{'
        matches = re.finditer(company_pattern, content)
        
        company_display_names = {}
        for match in matches:
            comment = match.group(1) if match.group(1) else None
            company_name = match.group(2)
            if comment and comment.strip():
                company_display_names[company_name] = comment.strip()
        
        # Now remove comments for parsing
        content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
        
        # Find all company definitions again for parsing
        company_pattern = r'(company_\w+)\s*=\s*\{'
        matches = re.finditer(company_pattern, content)
        
        for match in matches:
            company_name = match.group(1)
            start_pos = match.end() - 1  # Position of opening brace
            
            # Find matching closing brace
            brace_count = 0
            pos = start_pos
            while pos < len(content):
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        break
                pos += 1
            
            if brace_count == 0:
                company_content = content[start_pos+1:pos]  # Extract content between braces
                company_data = self.parse_company_data(company_name, company_content)
                
                # Add display name - prioritize manual mappings over game file comments
                # Complete wiki-based display name mappings (142 companies)
                display_names = {
                    'company_allatini_mills': 'Allatini Mills',
                    'company_altos_hornos_de_vizcaya': 'Altos Hornos de Vizcaya',
                    'company_anglo_persian_oil': 'Anglo-Persian Oil Company',
                    'company_anglo_sicilian_sulphur_company': 'Anglo-Sicilian Sulphur Company',
                    'company_ansaldo': 'Gio. Ansaldo & C.',
                    'company_ap_moller': 'A.P. Møller',
                    'company_argentinian_wine': 'Centro Vitivinícola Nacional',
                    'company_armstrong_whitworth': 'Sir W. G. Armstrong Whitworth & Co.',
                    'company_assam_company': 'Assam Company',
                    'company_b_grimm': 'B. Grimm',
                    'company_basf': 'BASF',
                    'company_basileiades': 'Basileiades',
                    'company_bengal_coal_company': 'Bengal Coal Company',
                    'company_bolckow_vaughan': 'Bolckow, Vaughan & Co.',
                    'company_bombay_burmah_trading_corporation': 'Bombay Burmah Trading Corporation',
                    'company_bombay_dyeing_company': 'Bombay Dyeing and Manufacturing Company Limited',
                    'company_branobel': 'Branobel',
                    'company_bunge_born': 'Bunge & Born',
                    'company_calcutta_electric': 'Calcutta Electric Supply Corporation Limited',
                    'company_caribbean_petroleum': 'Caribbean Petroleum Company',
                    'company_ccci': 'Compagnie du Congo',
                    'company_cfr': 'Căile Ferate Române',
                    'company_cgv': 'Confédération générale des vignerons',
                    'company_construction_power_bloc': 'United Construction Conglomerate',
                    'company_chr_hansens': 'Chr. Hansen',
                    'company_colt_firearms': 'Colt\'s Patent Firearms Manufacturing Company',
                    'company_compania_sansinena_de_carnes_congeladas': 'Compañía Sansinena de Carnes Congeladas',
                    'company_cordoba_railway': 'Ferrocarril Central Córdoba',
                    'company_csfa': 'Compañía de Salitres y Ferrocarril de Antofagasta',
                    'company_da_afghan_nassaji_sherkat': 'Də Afḡān Nasājī Šerkat',
                    'company_david_sassoon': 'David Sassoon & Co., Ltd',
                    'company_de_beers': 'De Beers Consolidated Mines Ltd.',
                    'company_dmc': 'Dollfus-Mieg et Compagnie',
                    'company_duro_y_compania': 'Duro y Compañía',
                    'company_east_india_company': 'East India Company',
                    'company_eea': 'Empresas Eléctricas Asociadas',
                    'company_egyptian_rail': 'Egyptian State Railways',
                    'company_el_aguila': 'El Águila',
                    'company_electricidad_de_caracas': 'C.A. La Electricidad de Caracas',
                    'company_ericsson': 'Ericsson',
                    'company_espana_industrial': 'La España Industrial',
                    'company_estaleiro_maua': 'Estaleiro Mauá',
                    'company_estanifera_llallagua': 'Compañía Estañífera de Llallagua',
                    'company_famae': 'Fábrica de Armas de la Nación',
                    'company_fcm': 'Forges et Chantiers de la Méditerranée',
                    'company_fiat': 'FIAT',
                    'company_foochow_arsenal': 'Foochow Shipyards',
                    'company_ford_motor': 'Ford Motor Company',
                    'company_franco_belge': 'Société Franco-Belge',
                    'company_fundicao_ipanema': 'Fundição Ipanema',
                    'company_fundidora_monterrey': 'Fundidora de Fierro y Acero de Monterrey',
                    'company_galician_carpathian_oil': 'Galician Carpathian Petroleum Company',
                    'company_gebruder_thonet': 'Gebrüder Thonet',
                    'company_general_electric': 'General Electric',
                    'company_gotaverken': 'Götaverken',
                    'company_great_indian_railway': 'Great Indian Peninsula Railway',
                    'company_guinness': 'Arthur Guinness Son & Co. Ltd',
                    'company_gwr': 'Great Western Railway',
                    'company_hanseong_jeongi_hoesa': 'Hanseong Jeongi Hoesa',
                    'company_hanyang_arsenal': 'Hanyang Arsenal',
                    'company_hbc': 'Hudson\'s Bay Company',
                    'company_ilva': 'Ilva',
                    'company_imperial_arsenal': 'Tersâne-i Âmire',
                    'company_imperial_ethiopian_railways': 'Imperial Ethiopian Railway Company',
                    'company_imperial_tobacco': 'Imperial Tobacco Corporation of Persia',
                    'company_iranian_state_railway': 'Iranian State Railway',
                    'company_izhevsk_arms_plant': 'Izhevsk Arms Plant',
                    'company_j_p_coats': 'J. & P. Coats',
                    'company_jiangnan_weaving_bureaus': 'Jiangnan Weaving Bureaus',
                    'company_jingdezhen': 'Jingdezhen Kilns',
                    'company_john_brown': 'John Brown & Company',
                    'company_john_cockerill': 'Société anonyme John Cockerill',
                    'company_john_holt': 'John Holt and Company',
                    'company_john_hughes': 'New Russia Company Ltd.',
                    'company_kablin': 'Klabin Irmãos & Cia.',
                    'company_kaiping_mining': 'Kaiping Mining Company',
                    'company_kinkozan_sobei': 'Kinkozan Sobei',
                    'company_kirgizian_mining_company': 'Kirgizian Mining Joint Stock Company',
                    'company_konigliche_porzellan_manufaktur_meissen': 'Königliche Porzellan-Manufaktur Meissen',
                    'company_kouppas': 'Kouppas',
                    'company_krupp': 'Friedrich Krupp',
                    'company_la_rosada': 'La Rosada',
                    'company_lanfang_kongsi': 'Lanfang Kongsi',
                    'company_lee_wilson': 'Lee Wilson & Company',
                    'company_lilpop': 'Lilpop, Rau i Loewenstein',
                    'company_lkab': 'LKAB',
                    'company_ludwig_moser_and_sons': 'Glasfabrik Ludwig Moser & Söhne',
                    'company_madura_mills': 'Madura Mills Co. Ltd',
                    'company_maison_worth': 'Maison Worth',
                    'company_manfred_weiss': 'Manfréd Weiss Steel and Metal Works',
                    'company_mantetsu': 'South Manchuria Railway',
                    'company_mantero_seta': 'Mantero Sera',
                    'company_maple_and_co': 'Maple & Co.',
                    'company_massey_harris': 'Massey-Harris Limited',
                    'company_mav': 'MÁVAG',
                    'company_mines_anzin': 'Compagnie des mines d\'Anzin',
                    'company_misr': 'Misr Spinning and Weaving Company',
                    'company_mitsubishi': 'Mitsubishi',
                    'company_mitsui': 'Mitsui',
                    'company_moscow_irrigation_company': 'Moscow Irrigation Company',
                    'company_mozambique_company': 'Companhia de Moçambique',
                    'company_nam_dinh': 'Nam Định Textile Factory',
                    'company_national_iranian_oil': 'National Iranian Oil Company',
                    'company_nederlandse_petroleum': 'Nederlandse Petroleum Maatschappij',
                    'company_nicolas_portalis': 'MM. Nicolas Portalis et Cie.',
                    'company_nokia': 'Nokia',
                    'company_norsk_hydro': 'Norsk Hydroelektrisk Kvælstofaktieselskap',
                    'company_oevg': 'Österreichische Waffenfabriks-Gesellschaft',
                    'company_ong_lung_sheng_tea_company': 'Ong Lung Sheng Tea Company',
                    'company_opium_export_monopoly': 'Bongāh-e Enḥeṣār-e Ṣāderāt-e Taryāk',
                    'company_orient_express': 'Chemins de fer Orientaux',
                    'company_oriental_development_company': 'Oriental Development Company',
                    'company_ottoman_tobacco_regie': 'Ottoman Tobacco Company',
                    'company_panama_company': 'Panama Canal Company',
                    'company_paradox': 'John Paradox & Company',
                    'company_pernambuco_textiles': 'Companhia Fiação e Tecidos de Pernambuco',
                    'company_perskhlopok': 'Perskhlopok',
                    'company_persshelk': 'Persshelk',
                    'company_peruvian_amazon': 'Peruvian Amazon Company',
                    'company_philips': 'Philips',
                    'company_prussian_state_railways': 'Preußische Staatseisenbahnen',
                    'company_putilov_company': 'Society of Putilov Factories',
                    'company_ralli_brothers': 'Ralli Brothers',
                    'company_rheinmetall': 'Rheinmetall',
                    'company_ricordi': 'G. Ricordi & C.',
                    'company_romanian_star': 'Steaua Română',
                    'company_rossi': 'Amadeo Rossi & Cia.',
                    'company_russian_american_company': 'Russian-American Company',
                    'company_saint_etienne': 'Manufacture d\'armes de Saint-Étienne',
                    'company_san_miguel': 'San Miguel',
                    'company_sao_paulo_railway': 'São Paulo Railway Co. Ltd.',
                    'company_savva_morozov': 'Savva Morozov & Sons',
                    'company_schichau': 'F. Schichau',
                    'company_schneider_creusot': 'Schneider et Cie',
                    'company_sherkat_shemali': 'Šerkat-e Etteḥādīya-ye Welāyat-e Šemālī',
                    'company_sherkate_eslamiya': 'Šerkat-e Eslāmiya',
                    'company_siemens_and_halske': 'Siemens & Halske',
                    'company_skoda': 'Škoda Works',
                    'company_societe_mokta_el_hadid': 'Société Mokta El Hadid',
                    'company_standard_oil': 'Standard Oil',
                    'company_steel_brothers': 'Steel Brothers & Co. Ltd',
                    'company_stt': 'Stabilimento Tecnico Triestino',
                    'company_sudamericana_de_vapores': 'Compañía Sudamericana de Vapores',
                    'company_suez_company': 'Suez Canal Company',
                    'company_sunhwaguk': 'Sunhwaguk',
                    'company_tashkent_railroad': 'Tashkent Railroad',
                    'company_tata': 'Tata',
                    'company_trubia': 'Fábrica de Armas de Trubia',
                    'company_turkish_petroleum': 'Turkish Petroleum Company',
                    'company_united_fruit': 'United Fruit Company',
                    'company_ursus': 'Ursus',
                    'company_us_steel': 'Carnegie Steel Co.',
                    'company_vodka_monopoly': 'Vodka Monopoly',
                    'company_wadia_shipbuilders': 'Wadia Shipbuilders',
                    'company_west_ural_petroleum': 'West Ural Petroleum Company, Limited',
                    'company_william_cramp': 'William Cramp & Sons',
                    'company_william_sandford': 'William Sandford Limited',
                    'company_zastava': 'Zastava',
                    # Final 14 edge cases for complete wiki coverage
                    'company_fundicao_ipanema': 'Fundição Ipanema',
                    'company_chr_hansens': 'Chr. Hansen',
                    'company_krupp': 'Friedrich Krupp',
                    'company_ansaldo': 'Gio. Ansaldo & C.',
                    'company_paradox': 'John Paradox & Company',
                    'company_afghan_national_weaving': 'Də Afḡān Nasājī Šerkat',
                    'company_north_league_company': 'Šerkat-e Etteḥādīya-ye Welāyat-e Šemālī',
                    'company_opium_export_monopoly': 'Bongāh-e Enḥeṣār-e Ṣāderāt-e Taryāk',
                    'company_islamic_company': 'Šerkat-e Eslāmiya',
                    'company_nam_dinh_textile': 'Nam Định Textile Factory',
                    'company_kirgizian_mining': 'Kirgizian Mining Joint Stock Company',
                    'company_tersane_i_amire': 'Tersâne-i Âmire',
                    'company_john_holt': 'John Holt and Company',
                    'company_portalis': 'MM. Nicolas Portalis et Cie.',
                }
                
                if company_name in display_names:
                    # Use manual mapping
                    company_data['display_name'] = display_names[company_name]
                elif company_name in company_display_names:
                    # Use game file comment
                    company_data['display_name'] = company_display_names[company_name]
                else:
                    # Fallback: clean up the company ID
                    display_name = company_name.replace('company_', '').replace('_', ' ').title()
                    company_data['display_name'] = display_name
                    
                companies[company_name] = company_data
                
        return companies

    def parse_company_data(self, company_name, company_content):
        """Parse individual company data"""
        company_data = {
            'building_types': [],
            'extension_building_types': [],
            'possible_prestige_goods': [],
            'flavored_company': 'flavored_company = yes' in company_content,
            'formation_requirements': [],
            'prestige_bonuses': [],
            'country': None,
            'country_confidence': 'none'
        }
        
        # Parse building types
        building_types_match = re.search(r'building_types\s*=\s*\{([^{}]+)\}', company_content)
        if building_types_match:
            buildings = re.findall(r'building_\w+', building_types_match.group(1))
            company_data['building_types'] = buildings
            
        # Parse extension building types
        extension_match = re.search(r'extension_building_types\s*=\s*\{([^{}]+)\}', company_content)
        if extension_match:
            buildings = re.findall(r'building_\w+', extension_match.group(1))
            company_data['extension_building_types'] = buildings
            
        # Parse prestige goods
        prestige_match = re.search(r'possible_prestige_goods\s*=\s*\{([^{}]+)\}', company_content)
        if prestige_match:
            prestige_goods = re.findall(r'prestige_good_\w+', prestige_match.group(1))
            company_data['possible_prestige_goods'] = prestige_goods
        
        # Parse formation requirements from possible block using brace matching
        possible_start = company_content.find('possible = {')
        if possible_start != -1:
            # Find the matching brace for the possible block
            brace_start = company_content.find('{', possible_start)
            if brace_start != -1:
                brace_count = 1
                pos = brace_start + 1
                while pos < len(company_content) and brace_count > 0:
                    if company_content[pos] == '{':
                        brace_count += 1
                    elif company_content[pos] == '}':
                        brace_count -= 1
                    pos += 1
                
                if brace_count == 0:
                    possible_content = company_content[brace_start+1:pos-1]
                    
                    # Extract state requirements and map to countries
                    state_regions = re.findall(r'state_region\s*=\s*s:(\w+)', possible_content)
                    
                    # Also extract region-based requirements (like sr:region_congo)
                    region_reqs = re.findall(r'region\s*=\s*sr:(\w+)', possible_content)
                    
                    formation_reqs = []
                    if state_regions:
                        # Remove duplicates and fix STATE_ prefix
                        unique_states = list(set(state_regions))
                        for state in unique_states:
                            # Don't add STATE_ prefix if it already exists
                            if state.startswith('STATE_'):
                                formation_reqs.append("Control state {}".format(state))
                            else:
                                formation_reqs.append("Control state STATE_{}".format(state.upper()))
                        
                    if region_reqs:
                        # Remove duplicates and add region requirements
                        unique_regions = list(set(region_reqs))
                        for region in unique_regions:
                            region_name = region.replace('_', ' ').title()
                            # Check for building level requirements in the same block
                            if 'level >= 5' in possible_content:
                                formation_reqs.append("Control region in {} (level 5+ buildings required)".format(region_name))
                            else:
                                formation_reqs.append("Control region in {}".format(region_name))
                    
                    # Extract additional requirements like state traits and building levels
                    if 'state_trait' in possible_content:
                        trait_matches = re.findall(r'has_state_trait\s*=\s*(\w+)', possible_content)
                        for trait in trait_matches:
                            trait_name = trait.replace('state_trait_', '').replace('_', ' ').title()
                            formation_reqs.append("States with {} trait".format(trait_name))
                    
                    # Extract building level requirements and deduplicate
                    building_level_matches = re.findall(r'is_building_type\s*=\s*(building_\w+).*?level\s*>=\s*(\d+)', possible_content, re.DOTALL)
                    building_requirements = set()  # Use set to avoid duplicates
                    for building, level in building_level_matches:
                        building_name = building.replace('building_', '').replace('_', ' ').title()
                        building_requirements.add("Level {}+ {} required".format(level, building_name))
                    
                    # Add unique building requirements to formation_reqs
                    formation_reqs.extend(sorted(building_requirements))
                    
                    # Extract culture requirements from potential block
                    potential_start = company_content.find('potential = {')
                    if potential_start != -1:
                        potential_brace_start = company_content.find('{', potential_start)
                        if potential_brace_start != -1:
                            brace_count = 1
                            pos = potential_brace_start + 1
                            while pos < len(company_content) and brace_count > 0:
                                if company_content[pos] == '{':
                                    brace_count += 1
                                elif company_content[pos] == '}':
                                    brace_count -= 1
                                pos += 1
                            
                            if brace_count == 0:
                                potential_content = company_content[potential_brace_start+1:pos-1]
                                
                                # Extract culture requirements
                                culture_reqs = re.findall(r'country_has_primary_culture\s*=\s*cu:(\w+)', potential_content)
                                for culture in culture_reqs:
                                    formation_reqs.append("Primary culture: {}".format(culture.replace('_', ' ').title()))
                                
                                # Extract direct country assignment (c:COUNTRY ?= this pattern)
                                country_assignment = re.search(r'c:(\w+)\s*\?\s*=\s*this', potential_content)
                                if country_assignment:
                                    assigned_country = country_assignment.group(1)
                                    company_data['country'] = assigned_country
                                    company_data['country_confidence'] = 'definitive'
                    
                    company_data['formation_requirements'] = formation_reqs
                        
                    # Map states to countries for country association
                    countries = []
                    if state_regions:
                        for state in state_regions:
                            if state in self.state_to_country:
                                base_country = self.state_to_country[state]
                                # Apply subject relationship mapping
                                effective_country = self.get_effective_country(base_country)
                                countries.append(effective_country)
                        
                        if countries:
                            # Use most common country (1836 game start ownership, with subject relationships)
                            country_counts = Counter(countries)
                            most_common_country = country_counts.most_common(1)[0][0]
                            company_data['country'] = most_common_country
                            company_data['country_confidence'] = 'definitive'  # From game files
                    
                    # Extract technology requirements
                    tech_reqs = re.findall(r'has_technology_researched\s*=\s*(\w+)', possible_content)
                    for tech in tech_reqs:
                        company_data['formation_requirements'].append("Technology: {}".format(tech.replace('_', ' ').title()))
        
        # Parse prestige bonuses from prosperity_modifier
        prosperity_match = re.search(r'prosperity_modifier\s*=\s*\{([^{}]+)\}', company_content)
        if prosperity_match:
            prosperity_content = prosperity_match.group(1)
            bonuses = []
            
            # Various bonus types
            throughput_matches = re.findall(r'building_(\w+)_throughput_add\s*=\s*([\d.]+)', prosperity_content)
            for building_name, value in throughput_matches:
                building_name = building_name.replace('_', ' ').title()
                bonuses.append("{} +{:.0f}% throughput".format(building_name, float(value)*100))
            
            employment_matches = re.findall(r'building_(\w+)_employment_add\s*=\s*([\d.]+)', prosperity_content)
            for building_name, value in employment_matches:
                building_name = building_name.replace('_', ' ').title()
                bonuses.append("{} +{:.0f}% employment".format(building_name, float(value)*100))
                
            # Output bonuses  
            output_matches = re.findall(r'(\w+)_output_add\s*=\s*([\d.]+)', prosperity_content)
            for good, value in output_matches:
                good_name = good.replace('_', ' ').title()
                bonuses.append("{} +{:.0f}% output".format(good_name, float(value)*100))
            
            # Input cost bonuses
            input_matches = re.findall(r'(\w+)_input_mult\s*=\s*([\d.-]+)', prosperity_content)
            for good, value in input_matches:
                good_name = good.replace('_', ' ').title()
                bonus_pct = (1 - float(value)) * 100
                bonuses.append("{} -{:.0f}% input cost".format(good_name, bonus_pct))
            
            company_data['prestige_bonuses'] = bonuses
        
        # Apply wiki-based country assignment (takes priority over game-file assignments)
        wiki_match = self.find_wiki_country_for_company(company_name)
        if wiki_match:
            company_data['country'] = wiki_match
            company_data['country_confidence'] = 'wiki_assignment'
            
        return company_data
    
    def parse_all_companies(self):
        """Parse all company files in the directory"""
        if not os.path.exists(self.company_types_dir):
            raise FileNotFoundError("Company types directory not found: {}".format(self.company_types_dir))
            
        for filename in os.listdir(self.company_types_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.company_types_dir, filename)
                print("Parsing {}...".format(filename))
                try:
                    import codecs
                    with codecs.open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    file_companies = self.parse_paradox_file(content)
                    
                    # Add file-based country inference for companies without state requirements
                    file_country = self.infer_country_from_filename(filename)
                    for company_name, company_data in file_companies.items():
                        if company_data['flavored_company'] and (not company_data.get('country') or company_data.get('country') == ''):
                            # Try manual override first
                            override_country = self.get_company_country_override(company_name)
                            if override_country:
                                company_data['country'] = override_country
                                company_data['country_confidence'] = 'manual_assignment'
                            elif file_country:
                                company_data['country'] = file_country
                                company_data['country_confidence'] = 'file_based'
                    
                    self.companies.update(file_companies)
                    
                    # Track all buildings
                    for company_data in file_companies.values():
                        self.all_buildings.update(company_data['building_types'])
                        self.all_buildings.update(company_data['extension_building_types'])
                        
                except Exception as e:
                    print("Error parsing {}: {}".format(file_path, e))
                continue
                
        print("Parsed {} companies with {} unique buildings".format(len(self.companies), len(self.all_buildings)))
        
        # Count flavored companies with country associations
        flavored_count = sum(1 for data in self.companies.values() if data['flavored_company'])
        country_count = sum(1 for data in self.companies.values() if data['country'])
        print("Found {} flavored companies, {} with country associations".format(flavored_count, country_count))

    def get_building_frequency(self, companies):
        """Count how many companies use each building"""
        building_counts = Counter()
        
        for company_data in companies.values():
            for building in company_data['building_types']:
                building_counts[building] += 1
            for building in company_data['extension_building_types']:
                building_counts[building] += 1
                
        return building_counts
        
    def get_companies_with_building(self, building, as_extension=False, with_prestige=False):
        """Get all companies that have a specific building"""
        companies_with_building = []
        
        for company_name, data in self.companies.items():
            has_building = False
            has_prestige = False
            
            if as_extension:
                has_building = building in data['extension_building_types']
            else:
                has_building = building in data['building_types']
                
            # Check if this company can produce prestige goods for buildings it has as base
            if has_building and not as_extension and data['possible_prestige_goods']:
                # Use the same logic as company_has_prestige_for_building
                prestige_result = self.company_has_prestige_for_building(company_name, building)
                if prestige_result and isinstance(prestige_result, tuple) and prestige_result[0]:
                    has_prestige = True
                
            if has_building:
                if with_prestige and has_prestige:
                    companies_with_building.append((company_name, 'prestige'))
                elif not with_prestige:
                    companies_with_building.append((company_name, 'base' if not as_extension else 'extension'))
                    
        return companies_with_building
    
    def get_all_buildings_for_companies(self, company_names):
        """Get all buildings (base + extension) available to a set of companies"""
        all_buildings = set()
        
        for company_name in company_names:
            if company_name in self.companies:
                data = self.companies[company_name]
                all_buildings.update(data['building_types'])
                all_buildings.update(data['extension_building_types'])
                
        return sorted(all_buildings)
    
    def company_has_prestige_for_building(self, company_name, building):
        """Check if a company can produce prestige goods for this specific building"""
        if company_name not in self.companies:
            return False
            
        data = self.companies[company_name]
        if not data['possible_prestige_goods'] or building not in data['building_types']:
            return False
            
        # Get the good that this building produces
        building_good = self.building_to_goods.get(building)
        if not building_good:
            return False
            
        # Check if any prestige good matches this building's output
        for prestige_good in data['possible_prestige_goods']:
            if prestige_good in self.prestige_goods:
                base_good = self.prestige_goods[prestige_good]
                if base_good == building_good:
                    return True, prestige_good
                
                # Handle special cases for prestige goods that don't have direct building matches
                if self._prestige_good_matches_building(prestige_good, base_good, building, building_good):
                    return True, prestige_good
                    
        return False, None
    
    def _prestige_good_matches_building(self, prestige_good, base_good, building, building_good):
        """Handle the few essential special cases for prestige goods"""
        
        # Just the essential cases we identified
        if base_good == 'luxury_furniture' and building == 'building_furniture_manufacturies':
            return True
        if base_good == 'porcelain' and building == 'building_glassworks':
            return True
        if base_good in ['telephones', 'radios'] and building == 'building_electrics_industry':
            return True
        if base_good == 'automobiles' and building == 'building_automotive_industry':
            return True
        if base_good == 'luxury_clothes' and building == 'building_textile_mills':
            return True
        
        return False
    
    def cross_check_with_wiki(self):
        """Cross-check extracted country data with wiki data"""
        if not self.wiki_companies:
            print("No wiki data available for cross-checking")
            return
            
        print("\n=== Country Association Cross-Check ===")
        matches = 0
        mismatches = 0
        missing_from_extraction = 0
        
        # Check extracted companies against wiki
        for company_name, data in self.companies.items():
            if data['country']:
                wiki_key = company_name.replace('company_', '').replace('_', ' ').lower()
                
                if wiki_key in self.wiki_companies:
                    wiki_country = self.wiki_companies[wiki_key]
                    extracted_country = data['country']
                    confidence = data['country_confidence']
                    
                    if wiki_country == extracted_country:
                        print("✅ {}: {} ({})".format(company_name.replace('company_', '').replace('_', ' ').title(), extracted_country, confidence))
                        matches += 1
                    else:
                        print("❌ {}: Extracted {} ({}) vs Wiki {}".format(company_name.replace('company_', '').replace('_', ' ').title(), extracted_country, confidence, wiki_country))
                        mismatches += 1
                else:
                    print("INFO: {}: Extracted {} ({}), not in wiki".format(company_name.replace('company_', '').replace('_', ' ').title(), data['country'], data['country_confidence']))
        
        # Check for companies in wiki but not extracted
        for wiki_key, wiki_country in self.wiki_companies.items():
            found = False
            for company_name, data in self.companies.items():
                if company_name.replace('company_', '').replace('_', ' ').lower() == wiki_key and data['country']:
                    found = True
                    break
            if not found:
                company_display = wiki_key.title()
                print("WARNING: {}: Wiki has {}, but extraction found none".format(company_display, wiki_country))
                missing_from_extraction += 1
                
        print("\nSummary: {} matches, {} mismatches, {} missing from extraction".format(matches, mismatches, missing_from_extraction))

    def generate_html_report(self):
        """Generate HTML analysis report with all bugs fixed"""
        
        # Get building frequencies and order buildings logically based on Victoria 3 wiki
        building_counts = self.get_building_frequency(self.companies)
        
        # Define building order in user's preferred categorization
        wiki_building_order = [
            # Extraction
            'building_coal_mine',
            'building_fishing_wharf',
            'building_gold_mine',
            'building_iron_mine',
            'building_lead_mine',
            'building_logging_camp',
            'building_oil_rig',
            'building_rubber_plantation',
            'building_sulfur_mine',
            'building_whaling_station',
            
            # Manufacturing Industries
            'building_arms_industry',
            'building_artillery_foundries',
            'building_automotive_industry',
            'building_electrics_industry',
            'building_explosives_factory',
            'building_chemical_plants',
            'building_food_industry',
            'building_furniture_manufacturies',
            'building_glassworks',
            'building_military_shipyards',
            'building_motor_industry',
            'building_munition_plants',
            'building_paper_mills',
            'building_shipyards',
            'building_steel_mills',
            'building_synthetics_plants',
            'building_textile_mills',
            'building_tooling_workshops',
            
            # Infrastructure + Urban Facilities
            'building_port',
            'building_railway', 
            'building_trade_center',
            'building_power_plant',
            'building_arts_academy',
            
            # Agriculture + Plantations + Ranches
            'building_maize_farm',
            'building_millet_farm', 
            'building_rice_farm',
            'building_rye_farm',
            'building_wheat_farm',
            'building_vineyard_plantation',
            'building_banana_plantation',
            'building_coffee_plantation', 
            'building_cotton_plantation',
            'building_dye_plantation',
            'building_opium_plantation',
            'building_silk_plantation',
            'building_sugar_plantation',
            'building_tea_plantation',
            'building_tobacco_plantation',
            'building_livestock_ranch'
        ]
        
        # Filter to only buildings we actually have companies for, preserving wiki order
        buildings_to_analyze = []
        for building in wiki_building_order:
            if building in self.all_buildings:
                buildings_to_analyze.append(building)
        
        # Add any remaining buildings we have that weren't in the wiki order (shouldn't happen but safety net)
        for building in sorted(self.all_buildings):
            if building not in buildings_to_analyze:
                buildings_to_analyze.append(building)
        
        html = u"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Victoria 3 Company Analysis Tool</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f8f6f1;
            color: #2c2416;
        }
        
        h1 {
            color: #8b4513;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.2em;
        }
        
        h2 {
            color: #8b4513;
            margin-top: 35px;
            padding: 12px 15px;
            background: #e6d7c3;
            border-left: 5px solid #8b6914;
            border-radius: 6px;
            font-size: 18px;
        }
        
        .building-summary {
            margin-bottom: 15px;
            color: #666;
            font-style: italic;
        }
        
        
        /* Description column styling for legend table */
        .description {
            font-size: 14px;
            color: #555;
            padding: 8px 12px;
        }
        
        /* Legend table specific overrides */
        #legend .building-table {
            width: auto;
            min-width: 500px;
            max-width: none;
        }
        
        #legend .table-container {
            overflow-x: visible;
            width: auto;
        }
        
        #legend th, #legend td {
            white-space: nowrap;
            min-width: auto;
        }
        
        #legend .company-header, #legend .building-header {
            padding: 12px 20px;
        }
        
        #legend .company-name, #legend .description {
            padding: 12px 20px;
        }
        
        /* Make legend "Meaning" header match company name styling */
        #legend .company-header {
            text-align: left !important;
            font-weight: normal !important;
            padding: 12px 20px;
        }
        
        /* Company card tooltip - positioned above table, wider for 256px icon */
        .company-tooltip {
            position: absolute;
            background: #fff;
            border: 2px solid #8b4513;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            min-width: 650px;
            max-width: 800px;
            display: none;
            font-size: 14px;
        }
        
        .company-tooltip h3 {
            margin: 0 0 10px 0;
            color: #8b4513;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }
        
        /* Company icon in tooltip - 256x256 and positioned on the right */
        .company-tooltip .company-icon {
            width: 256px;
            height: 256px;
            border-radius: 12px;
            float: right;
            margin-left: 20px;
            margin-bottom: 10px;
            border: 3px solid #8b4513;
            background: #f5f3ed;
        }
        
        .company-tooltip .company-icon-placeholder {
            width: 256px;
            height: 256px;
            background: #e8e2d4;
            border: 3px dashed #bbb;
            border-radius: 8px;
            float: right;
            margin-left: 20px;
            margin-bottom: 10px;
        }
        
        .company-tooltip .company-details {
            display: block;
            margin-right: 286px; /* Make room for the 256px icon + margins on the right */
        }
        
        .company-tooltip .requirements, .company-tooltip .bonuses, 
        .company-tooltip .prestige-goods, .company-tooltip .base-buildings, 
        .company-tooltip .industry-charters {
            margin-top: 10px;
        }
        
        .company-tooltip .requirements h4, .company-tooltip .bonuses h4,
        .company-tooltip .prestige-goods h4, .company-tooltip .base-buildings h4,
        .company-tooltip .industry-charters h4 {
            margin: 0 0 5px 0;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
        }
        
        .company-tooltip ul {
            margin: 0;
            padding-left: 15px;
            font-size: 13px;
        }
        
        /* Fixed table container - prevent horizontal stretch */
        .table-container {
            overflow-x: auto;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 100%;
        }
        
        .building-table {
            border-collapse: collapse !important;
            background-color: white;
            table-layout: fixed !important;
            width: auto !important;
            max-width: none !important;
            min-width: 0 !important;
        }
        
        .building-table th, .building-table td {
            padding: 8px;
            text-align: center;
            border-bottom: 1px solid #e0ddd4;
            white-space: nowrap;
        }
        
        .building-table th {
            background-color: #d2b48c;
            color: #2c2416;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 5;
        }
        
        .building-table tr:hover {
            background-color: #f5f3ed;
        }
        
        /* Company name column - ABSOLUTE FIXED WIDTH */
        table.building-table th.company-name,
        table.building-table td.company-name,
        .building-table th.company-name,
        .building-table td.company-name,
        th.company-name,
        td.company-name {
            width: 300px !important;
            min-width: 300px !important;
            max-width: 300px !important;
            text-align: left !important;
            font-weight: 500 !important;
            cursor: pointer !important;
            padding: 8px !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }
        
        /* Company icon styling */
        .company-icon {
            width: 24px;
            height: 24px;
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
            border-radius: 4px;
        }
        
        .company-icon-placeholder {
            width: 24px;
            height: 24px;
            background: #e8e2d4;
            border: 1px dashed #bbb;
            border-radius: 4px;
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
        }
        
        /* Sortable table styling */
        table.sortable th {
            cursor: pointer;
            user-select: none;
            position: relative;
        }
        
        table.sortable th:hover {
            background-color: #c4a373;
        }
        
        table.sortable th.sort-asc::after {
            content: ' ▲';
            font-size: 12px;
            color: #666;
        }
        
        table.sortable th.sort-desc::after {
            content: ' ▼';
            font-size: 12px;
            color: #666;
        }
        
        /* AGGRESSIVE COLUMN WIDTH ENFORCEMENT */
        table.building-table,
        .building-table,
        table.building-table *,
        .building-table * {
            box-sizing: border-box !important;
        }
        
        /* Flag column - ABSOLUTE FIXED WIDTH - NARROWER */
        table.building-table th.flag-column,
        table.building-table td.flag-column,
        .building-table th.flag-column,
        .building-table td.flag-column,
        th.flag-column,
        td.flag-column {
            width: 50px !important;
            min-width: 50px !important;
            max-width: 50px !important;
            text-align: center !important;
            font-size: 18px !important;
            padding: 2px !important;
            overflow: hidden !important;
            white-space: nowrap !important;
        }
        
        /* Buildings count column - ABSOLUTE FIXED WIDTH - NARROWER */
        table.building-table th.buildings-column,
        table.building-table td.buildings-column,
        .building-table th.buildings-column,
        .building-table td.buildings-column,
        th.buildings-column,
        td.buildings-column {
            width: 60px !important;
            min-width: 60px !important;
            max-width: 60px !important;
            text-align: center !important;
            padding: 2px !important;
            overflow: hidden !important;
            white-space: nowrap !important;
        }
        
        /* Removed duplicate rules - handled above with aggressive selectors */
        
        .prestige-icon {
            width: 20px;
            height: 20px;
            display: inline-block;
            vertical-align: middle;
            margin-right: 4px;
        }
        
        /* Removed duplicate header rule - handled above */
        
        /* Removed duplicate table rules - handled above with aggressive selectors */
        
        /* Building columns - ABSOLUTE FIXED WIDTH */
        table.building-table th:not(.flag-column):not(.buildings-column):not(.company-name),
        table.building-table td:not(.flag-column):not(.buildings-column):not(.company-name),
        .building-table th:not(.flag-column):not(.buildings-column):not(.company-name),
        .building-table td:not(.flag-column):not(.buildings-column):not(.company-name) {
            width: 50px !important;
            min-width: 50px !important;
            max-width: 50px !important;
            text-align: center !important;
            padding: 4px !important;
            overflow: hidden !important;
            white-space: nowrap !important;
        }
        
        /* Removed duplicate company name rules - handled above */
        
        .company-name:hover {
            /* Remove underline to avoid link-like appearance */
        }
        
        .building-header {
            width: 50px;
            min-width: 50px;
            max-width: 50px;
            height: 50px;
            background-size: 40px 40px;
            background-repeat: no-repeat;
            background-position: center;
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            position: relative;
        }
        
        .building-header.missing-icon {
            background-image: none;
        }
        
        .building-header.missing-icon::after {
            content: "❌";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 20px;
        }
        
        .building-icon {
            display: none; /* Hidden since we're using background images */
        }
        
        .missing-building-icon {
            display: none; /* Hidden since we're using CSS pseudo-element */
        }
        
        .base-building {
            background-color: #E3F2FD;
            border: 1px solid #2196F3;
        }
        
        .extension-building {
            background-color: #FFF3E0;
            border: 1px solid #FF9800;
        }
        
        .prestige-building {
            background: linear-gradient(135deg, #BBDEFB, #90CAF9);
            border: 2px solid #1976D2;
            box-shadow: 0 0 8px rgba(25, 118, 210, 0.4);
            font-weight: bold;
            color: #0D47A1;
        }
        
        .toc {
            background: #f0ebe3;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #d4c5a9;
            margin-bottom: 30px;
        }
        
        .toc h3 {
            color: #8b4513;
            margin-top: 0;
            margin-bottom: 15px;
        }
        
        /* Three-column flexbox layout */
        .toc-columns {
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }
        
        .toc-column {
            flex: 1;
            min-width: 0; /* Allow shrinking */
            overflow: hidden;
        }
        
        .toc-column ul {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        
        .toc li {
            margin-bottom: 5px;
            break-inside: avoid;
        }
        
        .toc a {
            color: #6b4423;
            text-decoration: none;
            font-size: 14px;
        }
        
        .toc a:hover {
            text-decoration: underline;
        }
        
        /* Category headers in table of contents */
        .category-header {
            font-weight: bold;
            color: #8b4513;
            margin-top: 15px;
            margin-bottom: 5px;
            font-size: 15px;
            border-bottom: 1px solid #d4c5a9;
            padding-bottom: 3px;
        }
        
        .category-header:first-child {
            margin-top: 0;
        }
        
        /* Category items in table of contents */
        .category-item {
            margin-bottom: 3px;
        }
        
        .category-item a {
            font-size: 13px;
            display: flex;
            align-items: center;
        }
        
        /* Building icons in table of contents */
        .toc-building-icon {
            width: 18px;
            height: 18px;
            margin-right: 6px;
            flex-shrink: 0;
        }
        
        /* Back to top link styling */
        .back-to-top {
            float: right;
            font-size: 14px;
            color: #666;
            text-decoration: none;
            font-weight: normal;
            margin-left: 20px;
        }
        
        .back-to-top:hover {
            color: #0066cc;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1 id="top">Victoria 3 Company Analysis Tool</h1>
    
    <!-- Company tooltip -->
    <div id="companyTooltip" class="company-tooltip"></div>
    
    <div class="toc">
        <a name="buildings"></a>
        <h3 id="buildings">Buildings</h3>
        <div class="toc-columns">"""
        
        # Define three-column layout: Left + Middle + Right
        column_groups = [
            # Left Column: Extraction + Infrastructure + Urban Facilities
            [
                ("Extraction", [
                    'building_coal_mine', 'building_fishing_wharf', 'building_gold_mine', 'building_iron_mine',
                    'building_lead_mine', 'building_logging_camp', 'building_oil_rig', 'building_rubber_plantation',
                    'building_sulfur_mine', 'building_whaling_station'
                ]),
                ("Infrastructure + Urban Facilities", [
                    'building_port', 'building_railway', 'building_trade_center', 'building_power_plant',
                    'building_arts_academy'
                ])
            ],
            # Middle Column: Manufacturing Industries
            [
                ("Manufacturing Industries", [
                    'building_arms_industry', 'building_artillery_foundries', 'building_automotive_industry',
                    'building_electrics_industry', 'building_explosives_factory', 'building_chemical_plants',
                    'building_food_industry', 'building_furniture_manufacturies', 'building_glassworks',
                    'building_military_shipyards', 'building_motor_industry', 'building_munition_plants',
                    'building_paper_mills', 'building_shipyards', 'building_steel_mills', 'building_synthetics_plants',
                    'building_textile_mills', 'building_tooling_workshops'
                ])
            ],
            # Right Column: Agriculture + Plantations + Ranches
            [
                ("Agriculture + Plantations + Ranches", [
                    'building_maize_farm', 'building_millet_farm', 'building_rice_farm', 'building_rye_farm',
                    'building_wheat_farm', 'building_vineyard_plantation', 'building_banana_plantation',
                    'building_coffee_plantation', 'building_cotton_plantation', 'building_dye_plantation',
                    'building_opium_plantation', 'building_silk_plantation', 'building_sugar_plantation',
                    'building_tea_plantation', 'building_tobacco_plantation', 'building_livestock_ranch'
                ])
            ]
        ]
        
        # Generate each column
        for column_categories in column_groups:
            html += '<div class="toc-column"><ul>'
            
            for category_name, category_buildings in column_categories:
                # Add category header
                html += '<li class="category-header">{}</li>'.format(category_name)
                
                # Add buildings in this category
                for building in category_buildings:
                    if building in buildings_to_analyze:
                        display_name = building.replace('building_', '').replace('_', ' ').title()
                        usage_count = building_counts.get(building, 0)
                        anchor_name = "building-{}".format(building)
                        # Use the existing building icon path method
                        icon_path = self.get_building_icon_path(building)
                        if not icon_path:
                            # Fallback if icon not found
                            building_key = building.replace('building_', '')
                            icon_path = "buildings/64px-Building_{}.png".format(building_key)
                        html += '<li class="category-item"><a href="#{}">' \
                               '<img src="{}" class="toc-building-icon" alt="{} icon">{} ({})' \
                               '</a></li>'.format(anchor_name, icon_path, display_name, display_name, usage_count)
            
            html += '</ul></div>'
        
        html += '''
        </div>
    </div>'''
        
        # Add Legend/Key table
        html += '''
    <!-- Legend/Key Table -->
    <div id="legend" class="building-section">
        <h2>Symbol Legend</h2>
        <div class="table-container">
            <table class="building-table">
                <thead>
                    <tr>
                        <th class="company-header">Meaning</th>
                        <th class="building-header" style="min-width: 120px;">e.g.</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="company-name">Prestige Good</td>
                        <td class="prestige-building"><img src="icons/24px-Prestige_ford_automobiles.png" width="16" height="16" alt="Prestige Good Example" title="Prestige Good"></td>
                    </tr>
                    <tr>
                        <td class="company-name">Base Building</td>
                        <td class="base-building">&#x25CF;</td>
                    </tr>
                    <tr>
                        <td class="company-name">Industry Charter</td>
                        <td class="extension-building">&#x25CB;</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>'''
        
        # Generate separate table for each building
        for building in buildings_to_analyze:
            display_name = building.replace('building_', '').replace('_', ' ').title()
            anchor_name = "building-{}".format(building)
            usage_count = building_counts.get(building, 0)
            
            # Get companies that have this building
            companies_with_base = self.get_companies_with_building(building, as_extension=False)
            companies_with_extension = self.get_companies_with_building(building, as_extension=True)
            companies_with_prestige = self.get_companies_with_building(building, with_prestige=True)
            
            # Combine all companies for this building
            all_companies_with_building = set()
            for company, _ in companies_with_base + companies_with_extension + companies_with_prestige:
                all_companies_with_building.add(company)
            
            if not all_companies_with_building:
                continue
            
            # Get all buildings available to these companies (for columns) - frequency ordered by usage within this company set
            available_buildings = self.get_all_buildings_for_companies(all_companies_with_building)
            
            # Count usage within this specific company set
            company_specific_counts = Counter()
            for company_name in all_companies_with_building:
                if company_name in self.companies:
                    data = self.companies[company_name]
                    for b in data['building_types']:
                        company_specific_counts[b] += 1
                    for b in data['extension_building_types']:
                        company_specific_counts[b] += 1
            
            # Sort buildings by usage frequency within this company set (most used first)
            available_buildings = sorted(available_buildings, key=lambda b: (-company_specific_counts.get(b, 0), b))
            
            # Get building icon for header
            building_icon_path = self.get_building_icon_path(building)
            building_icon_html = ''
            if building_icon_path:
                building_icon_html = '<img src="{}" style="width:32px;height:32px;vertical-align:middle;margin-right:10px;" alt="{} icon">'.format(building_icon_path, display_name)
            
            html += '''
    <h2 id="{}">{}{} <a href="#buildings" class="back-to-top" title="Back to Table of Contents">↑ Back to Top</a></h2>
    <p class="building-summary">Companies that can utilize this building: {}</p>
    
    <div class="table-container">
        <table class="building-table sortable">
            <thead>
                <tr>
                    <th class="flag-column" title="Country">🏳️</th>
                    <th class="buildings-column" title="Base Coverage . Available Industry Charters">📊</th>
                    <th class="company-name">Company Name</th>'''.format(anchor_name, building_icon_html, display_name, len(all_companies_with_building))
            
            # Add columns for all buildings these companies can use (frequency ordered within this company set)
            for avail_building in available_buildings:
                icon_path = self.get_building_icon_path(avail_building)
                avail_display = avail_building.replace('building_', '').replace('_', ' ').title()
                usage_in_set = company_specific_counts.get(avail_building, 0)
                
                if icon_path:
                    header_style = 'style="background-image: url({})"'.format(icon_path)
                    header_class = 'building-header'
                else:
                    header_style = ''
                    header_class = 'building-header missing-icon'
                
                html += '''
                    <th class="{}" {} title="{} ({} companies)">
                    </th>'''.format(header_class, header_style, avail_display, usage_in_set)
            
            html += '''
                </tr>
            </thead>
            <tbody>'''
            
            # Sort companies by building priority for this specific building
            def company_sort_key(company_name):
                data = self.companies[company_name]
                
                # Priority: companies with prestige > base > extension
                # Check if company has ANY prestige goods, not just for this specific building
                has_prestige = bool(data.get('possible_prestige_goods', []))
                has_base = building in data['building_types']
                has_extension = building in data['extension_building_types']
                
                priority = 0
                if has_prestige:
                    priority = 3
                elif has_base:
                    priority = 2  
                elif has_extension:
                    priority = 1
                
                # Get building counts for secondary sorting
                base_count, charter_count, _ = self.get_company_building_stats(company_name)
                total_buildings = base_count + charter_count
                
                # Sort by priority first, then by total building count (descending), then by charter count (descending)
                return (-priority, -total_buildings, -charter_count, company_name.replace('company_', '').lower())
            
            sorted_company_names = sorted(all_companies_with_building, key=company_sort_key)
            
            # Generate rows for this building's table
            for company_name in sorted_company_names:
                data = self.companies[company_name]
                display_name = data.get('display_name', self.get_company_display_name(company_name))
                
                # Abbreviate long company names for display
                abbreviated_name = self.abbreviate_company_name(display_name, 35)
                
                # Get company building statistics and prestige goods
                base_count, charter_count, prestige_goods = self.get_company_building_stats(company_name)
                building_count_display = self.format_building_count(base_count, charter_count)
                prestige_icons = self.get_company_prestige_icons(company_name)
                
                # Get company logo
                company_icon_path = self.get_company_icon_path(company_name)
                company_icon_html = ''
                if company_icon_path:
                    company_icon_html = '<img src="{}" class="company-icon" alt="Company Icon">'.format(company_icon_path)
                else:
                    company_icon_html = '<div class="company-icon-placeholder"></div>'
                
                # Get country flag for separate column with country name tooltip
                country_flag = ''
                country_name = ''
                if data['country']:
                    country_flag = self.get_country_flag(data['country'])
                    country_name = self.get_country_name(data['country'])
                
                flag_cell_html = ''
                if country_flag:
                    flag_cell_html = '<span title="{}">{}</span>'.format(country_name, country_flag)
                else:
                    flag_cell_html = ''
                
                html += '''
            <tr>
                <td class="flag-column">{}</td>
                <td class="buildings-column">{}</td>
                <td class="company-name"
                    onmouseover="showCompanyTooltip(event, '{}')" 
                    onmouseout="hideCompanyTooltip()" 
                    data-company="{}">
                    {}{}{}
                </td>'''.format(flag_cell_html, building_count_display, company_name, company_name, company_icon_html, prestige_icons, abbreviated_name)
                
                # Add columns for all available buildings
                for avail_building in available_buildings:
                    cell_content = ""
                    cell_class = ""
                    
                    # Check if company has this building and in what capacity
                    has_base = avail_building in data['building_types']
                    has_extension = avail_building in data['extension_building_types']
                    has_prestige_result = self.company_has_prestige_for_building(company_name, avail_building)
                    
                    if isinstance(has_prestige_result, tuple):
                        has_prestige, prestige_good = has_prestige_result
                    else:
                        has_prestige = has_prestige_result
                        prestige_good = None
                    
                    if has_prestige and prestige_good:
                        # Use prestige good icon with proper alt text
                        prestige_good_base = prestige_good.replace('prestige_good_generic_', '').replace('prestige_good_', '')
                        
                        # Special icon mappings for prestige goods that don't have exact icon matches
                        icon_mappings = {
                            'burmese_teak': 'teak',
                            'swedish_bar_iron': 'oregrounds_iron'
                        }
                        
                        if prestige_good_base in icon_mappings:
                            prestige_good_base = icon_mappings[prestige_good_base]
                        
                        # Try prestige-specific icon first, fallback to goods icon
                        prestige_icon_candidates = [
                            "icons/24px-Prestige_{}.png".format(prestige_good_base),
                            "icons/40px-Goods_{}.png".format(prestige_good_base)
                        ]
                        
                        prestige_icon_path = None
                        for candidate in prestige_icon_candidates:
                            full_path = os.path.join(os.path.dirname(__file__), candidate)
                            if os.path.exists(full_path):
                                prestige_icon_path = candidate
                                break
                        
                        if not prestige_icon_path:
                            prestige_icon_path = "icons/40px-Goods_services.png"  # Ultimate fallback
                        
                        prestige_name = self.prestige_good_names.get(prestige_good, prestige_good_base.replace('_', ' ').title())
                        cell_content = '<img src="{}" width="16" height="16" alt="{}" title="{}">'.format(prestige_icon_path, prestige_name, prestige_name)
                        cell_class = "prestige-building"
                    elif has_base:
                        cell_content = "&#x25CF;"
                        cell_class = "base-building"
                    elif has_extension:
                        cell_content = "&#x25CB;"
                        cell_class = "extension-building"
                    
                    try:
                        html += '<td class="{}">{}</td>'.format(cell_class, cell_content)
                    except UnicodeDecodeError:
                        html += '<td class="{}">&#x25CF;</td>'.format(cell_class)
                
                html += '</tr>'
            
            html += '''
            </tbody>
        </table>
    </div>'''
        
        html += '''
    
    <script>
        // Company data for tooltips
        const companyData = {'''
        
        # Add company data for tooltips
        company_entries = []
        for company_name, data in self.companies.items():
            display_name = data.get('display_name', self.get_company_display_name(company_name))
            requirements_json = json.dumps(data['formation_requirements'])
            bonuses_json = json.dumps(data['prestige_bonuses'])
            country_info = ""  # Remove confidence display - country is definitive from game files
            
            # Add building information for detailed tooltip
            prestige_goods_json = json.dumps(data.get('possible_prestige_goods', []))
            base_buildings_json = json.dumps(data.get('building_types', []))
            industry_charters_json = json.dumps(data.get('extension_building_types', []))
            
            entry = '''            {}: {{
                "name": {},
                "country": {},
                "country_confidence": {},
                "country_info": {},
                "requirements": {},
                "bonuses": {},
                "prestige_goods": {},
                "base_buildings": {},
                "industry_charters": {}
            }}'''.format(json.dumps(company_name), json.dumps(display_name), json.dumps(data["country"] or ""), json.dumps(data["country_confidence"]), json.dumps(country_info), requirements_json, bonuses_json, prestige_goods_json, base_buildings_json, industry_charters_json)
            company_entries.append(entry)
        
        html += ',\n'.join(company_entries)
        html += '''
        };
        
        function getCompanyIconPath(companyName) {
            // Remove company_ prefix for icon lookup
            const cleanName = companyName.replace('company_', '');
            
            // Historical company mappings (generated from Python version)
            const historicalMappings = {'''

        # Generate JavaScript object from Python historical_mappings
        for key, value in self.historical_mappings.items():
            html += f'\n                "{key}": "{value}",'
        
        html += '''
            };
            
            // Check if we have a specific mapping for historical companies
            if (historicalMappings[cleanName]) {
                return `companies/png/historical_company_icons/${historicalMappings[cleanName]}.png`;
            }
            
            // Basic companies are in the root png folder
            if (cleanName.startsWith('basic_')) {
                return `companies/png/${cleanName}.png`;
            } 
            
            // Default historical company path
            return `companies/png/historical_company_icons/${cleanName}.png`;
        }
        
        // Table sorting functionality
        function makeSortable(table) {
            var headers = table.querySelectorAll('th');
            headers.forEach(function(header, index) {
                header.addEventListener('click', function() {
                    sortTable(table, index);
                });
            });
        }
        
        function sortTable(table, columnIndex) {
            var tbody = table.querySelector('tbody');
            var rows = Array.from(tbody.querySelectorAll('tr'));
            var header = table.querySelectorAll('th')[columnIndex];
            
            // Determine sort direction
            var isAscending = !header.classList.contains('sort-asc');
            
            // Clear all sort indicators
            table.querySelectorAll('th').forEach(function(th) {
                th.classList.remove('sort-asc', 'sort-desc');
            });
            
            // Add sort indicator
            header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
            
            // Sort rows
            rows.sort(function(a, b) {
                var aCell = a.cells[columnIndex];
                var bCell = b.cells[columnIndex];
                
                var aValue = aCell.textContent.trim();
                var bValue = bCell.textContent.trim();
                
                // Handle numeric values (like building counts)
                var aNum = parseFloat(aValue);
                var bNum = parseFloat(bValue);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAscending ? aNum - bNum : bNum - aNum;
                }
                
                // Handle text values
                return isAscending ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
            });
            
            // Reorder rows in DOM
            rows.forEach(function(row) {
                tbody.appendChild(row);
            });
        }
        
        // Country display helper function
        function getCountryDisplayInfo(countryCode) {
            const countryMap = {
                'AUS': { flag: '🇦🇹', name: 'Austria-Hungary' },
                'BEL': { flag: '🇧🇪', name: 'Belgium' },
                'LUX': { flag: '🇱🇺', name: 'Luxembourg' },
                'CHI': { flag: '🇨🇳', name: 'China' },
                'USA': { flag: '🇺🇸', name: 'United States' },
                'GBR': { flag: '🇬🇧', name: 'Great Britain' },
                'FRA': { flag: '🇫🇷', name: 'France' },
                'DEU': { flag: '🇩🇪', name: 'Germany' },
                'PRU': { flag: '🇩🇪', name: 'Prussia' },
                'RUS': { flag: '🇷🇺', name: 'Russia' },
                'JAP': { flag: '🇯🇵', name: 'Japan' },
                'KOR': { flag: '🇰🇷', name: 'Korea' },
                'SWE': { flag: '🇸🇪', name: 'Sweden' },
                'NET': { flag: '🇳🇱', name: 'Netherlands' },
                'SPA': { flag: '🇪🇸', name: 'Spain' },
                'TUR': { flag: '🇹🇷', name: 'Ottoman Empire' },
                'BRZ': { flag: '🇧🇷', name: 'Brazil' },
                'MEX': { flag: '🇲🇽', name: 'Mexico' },
                'ARG': { flag: '🇦🇷', name: 'Argentina' },
                'CHL': { flag: '🇨🇱', name: 'Chile' },
                'SAR': { flag: '🇮🇹', name: 'Sardinia-Piedmont' },
                'EGY': { flag: '🇪🇬', name: 'Egypt' },
                'PER': { flag: '🇮🇷', name: 'Persia' },
                'ETH': { flag: '🇪🇹', name: 'Ethiopia' },
                'SAF': { flag: '🇿🇦', name: 'South Africa' },
                'HBC': { flag: '🇨🇦', name: 'Hudson\\'s Bay Company' },
                'GRE': { flag: '🇬🇷', name: 'Greece' },
                'NOR': { flag: '🇳🇴', name: 'Norway' },
                'DEN': { flag: '🇩🇰', name: 'Denmark' },
                'FIN': { flag: '🇫🇮', name: 'Finland' },
                'POR': { flag: '🇵🇹', name: 'Portugal' },
                'BOL': { flag: '🇧🇴', name: 'Bolivia' },
                'VNZ': { flag: '🇻🇪', name: 'Venezuela' },
                'COL': { flag: '🇨🇴', name: 'Colombia' },
                'SER': { flag: '🇷🇸', name: 'Serbia' },
                'ROM': { flag: '🇷🇴', name: 'Romania' },
                'WAL': { flag: '🏴󠁧󠁢󠁷󠁬󠁳󠁿', name: 'Wallachia' },
                'BAD': { flag: '🇩🇪', name: 'Baden' },
                'SAX': { flag: '🇩🇪', name: 'Saxony' },
                'LAN': { flag: '🇨🇳', name: 'Lanfang Republic' },
                'SIC': { flag: '🇮🇹', name: 'Two Sicilies' },
                'BIC': { flag: '🇮🇳', name: 'British India' },
                'IND': { flag: '🇮🇳', name: 'India' },
                'DAI': { flag: '🇻🇳', name: 'Dai Nam' },
                'PHI': { flag: '🇵🇭', name: 'Philippines' },
                'NSW': { flag: '🇦🇺', name: 'New South Wales' },
                'SIA': { flag: '🇹🇭', name: 'Siam' },
                'BUR': { flag: '🇲🇲', name: 'Burma' },
                'PRG': { flag: '🇵🇾', name: 'Paraguay' },
                'NPU': { flag: '🇵🇪', name: 'North Peru' },
                'PNI': { flag: '🇮🇹', name: 'Papal States' },
                'CLM': { flag: '🇨🇴', name: 'Gran Colombia' },
                'KUN': { flag: '🇦🇫', name: 'Kunduz' },
                'KOK': { flag: '🇺🇿', name: 'Kokand' },
                'OZH': { flag: '🇰🇿', name: 'Kazakh Khanate' },
                'ARB': { flag: '🇸🇦', name: 'Arabia' },
                'CON': { flag: '🇫🇷', name: 'French Congo' },
                'CAN': { flag: '🇨🇦', name: 'Canada' },
                'SOK': { flag: '🇳🇬', name: 'Sokoto Caliphate' },
                'AFG': { flag: '🇦🇫', name: 'Afghanistan' },
                'AST': { flag: '🇦🇺', name: 'Australia' },
                'ITA': { flag: '🇮🇹', name: 'Italy' },
                'PEU': { flag: '🇵🇪', name: 'Peru' },
                'POL': { flag: '🇵🇱', name: 'Poland' }
            };
            return countryMap[countryCode] || { flag: '🏳️', name: countryCode };
        }
        
        // Tooltip performance optimization - cache and debouncing
        let tooltipCache = {};
        let tooltipTimeout;
        
        // Tooltip functions - must be global for inline event handlers
        function showCompanyTooltip(event, companyName) {
            // Clear any pending hide timeout
            if (tooltipTimeout) {
                clearTimeout(tooltipTimeout);
            }
            
            const tooltip = document.getElementById('companyTooltip');
            
            if (!tooltip) {
                console.error('Tooltip element not found!');
                return;
            }
            
            if (typeof companyData === 'undefined') {
                console.error('companyData is undefined!');
                return;
            }
            
            const data = companyData[companyName];
            
            if (!data) {
                return;
            }
            
            // Use cached content if available
            let html = tooltipCache[companyName];
            if (!html) {
                // Generate tooltip content once and cache it
                const iconPath = getCompanyIconPath(companyName);
                const iconElement = iconPath ? 
                    `<img src="${iconPath}" class="company-icon">` : 
                    '<span class="company-icon-placeholder"></span>';
                
                // Get country flag and full name (only for non-basic companies with countries)
                let countryDisplay = '';
                if (data.country && data.country !== '') {
                    const countryInfo = getCountryDisplayInfo(data.country);
                    if (countryInfo && countryInfo.name !== data.country) { // Only show if we have a proper country name
                        countryDisplay = `<br><small>Country: ${countryInfo.flag} ${countryInfo.name}</small>`;
                    }
                }
                
                html = `
                    <h3>
                        ${iconElement}
                        <div class="company-details">
                            ${data.name}
                            ${countryDisplay}
                        </div>
                    </h3>
                `;
                
                if (data.requirements && data.requirements.length > 0) {
                    html += '<div class="requirements"><h4>Formation Requirements</h4><ul>';
                    data.requirements.forEach(req => {
                        html += `<li>${req}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                if (data.bonuses && data.bonuses.length > 0) {
                    html += '<div class="bonuses"><h4>Prestige Bonuses</h4><ul>';
                    data.bonuses.forEach(bonus => {
                        html += `<li>${bonus}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // Add prestige goods section with icons
                if (data.prestige_goods && data.prestige_goods.length > 0) {
                    html += '<div class="prestige-goods"><h4>Prestige Goods</h4><ul>';
                    data.prestige_goods.forEach(good => {
                        // Get prestige good icon
                        const prestigeGoodBase = good.replace('prestige_good_generic_', '').replace('prestige_good_', '');
                        
                        // Icon mappings for prestige goods that don't have exact matches
                        const iconMappings = {
                            'burmese_teak': 'teak',
                            'swedish_bar_iron': 'oregrounds_iron'
                        };
                        
                        const mappedBase = iconMappings[prestigeGoodBase] || prestigeGoodBase;
                        const prestigeIcon = `icons/24px-Prestige_${mappedBase}.png`;
                        const fallbackIcon = `icons/40px-Goods_${mappedBase}.png`;
                        
                        const goodDisplayName = good.replace('prestige_good_generic_', '').replace('prestige_good_', '').replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                        
                        html += `<li><img src="${prestigeIcon}" width="16" height="16" style="margin-right: 6px; vertical-align: middle;" 
                                 onerror="this.src='${fallbackIcon}'; this.onerror=null;">${goodDisplayName}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // Add base buildings section with icons
                if (data.base_buildings && data.base_buildings.length > 0) {
                    html += '<div class="base-buildings"><h4>Base Buildings</h4><ul>';
                    data.base_buildings.forEach(building => {
                        const buildingName = building.replace('building_', '').replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                        
                        // Building name mappings for icon files that have different names
                        const buildingMappings = {
                            'building_chemical_plants': 'chemicals_industry',
                            'building_textile_mills': 'textile_industry', 
                            'building_artillery_foundries': 'artillery_foundry',
                            'building_automotive_industry': 'vehicles_industry',
                            'building_livestock_ranch': 'cattle_ranch',
                            'building_rubber_plantation': 'rubber_lodge',
                            'building_vineyard_plantation': 'vineyards'
                        };
                        
                        const mappedBuilding = buildingMappings[building] || building.replace('building_', '');
                        const buildingIcon = `buildings/64px-Building_${mappedBuilding}.png`;
                        
                        html += `<li><img src="${buildingIcon}" width="16" height="16" style="margin-right: 6px; vertical-align: middle;" 
                                 onerror="this.style.display='none';">${buildingName}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // Add possible industry charters section with icons
                if (data.industry_charters && data.industry_charters.length > 0) {
                    html += '<div class="industry-charters"><h4>Possible Industry Charters</h4><ul>';
                    data.industry_charters.forEach(charter => {
                        const charterName = charter.replace('building_', '').replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                        
                        // Building name mappings for icon files that have different names
                        const buildingMappings = {
                            'building_chemical_plants': 'chemicals_industry',
                            'building_textile_mills': 'textile_industry', 
                            'building_artillery_foundries': 'artillery_foundry',
                            'building_automotive_industry': 'vehicles_industry',
                            'building_livestock_ranch': 'cattle_ranch',
                            'building_rubber_plantation': 'rubber_lodge',
                            'building_vineyard_plantation': 'vineyards'
                        };
                        
                        const mappedCharter = buildingMappings[charter] || charter.replace('building_', '');
                        const charterIcon = `buildings/64px-Building_${mappedCharter}.png`;
                        
                        html += `<li><img src="${charterIcon}" width="16" height="16" style="margin-right: 6px; vertical-align: middle;" 
                                 onerror="this.style.display='none';">${charterName}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // Cache the generated content
                tooltipCache[companyName] = html;
            }
            
            tooltip.innerHTML = html;
            tooltip.style.display = 'block';
            
            // Smart tooltip positioning to stay within viewport bounds
            const rect = event.target.getBoundingClientRect();
            const tooltipRect = tooltip.getBoundingClientRect();
            
            // Get viewport dimensions and scroll position
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
            const scrollY = window.pageYOffset || document.documentElement.scrollTop;
            
            // Calculate initial position (above and to the left of cursor)
            let left = event.pageX - 20;
            let top = event.pageY - tooltipRect.height - 10;
            
            // Horizontal boundary detection and adjustment
            const rightEdge = left + tooltipRect.width;
            const leftEdge = left;
            const viewportRight = scrollX + viewportWidth;
            const viewportLeft = scrollX;
            
            if (rightEdge > viewportRight) {
                // Tooltip goes off right edge, move it left
                left = viewportRight - tooltipRect.width - 10;
            }
            if (leftEdge < viewportLeft) {
                // Tooltip goes off left edge, move it right
                left = viewportLeft + 10;
            }
            
            // Vertical boundary detection and adjustment
            const topEdge = top;
            const bottomEdge = top + tooltipRect.height;
            const viewportTop = scrollY;
            const viewportBottom = scrollY + viewportHeight;
            
            if (topEdge < viewportTop) {
                // Tooltip goes off top edge, show below cursor instead
                top = event.pageY + 20;
                // Check if it now goes off bottom edge
                if (top + tooltipRect.height > viewportBottom) {
                    // If it still doesn't fit, position at bottom of viewport
                    top = viewportBottom - tooltipRect.height - 10;
                }
            } else if (bottomEdge > viewportBottom) {
                // Tooltip goes off bottom edge, try to fit above
                const newTop = event.pageY - tooltipRect.height - 10;
                if (newTop >= viewportTop) {
                    top = newTop;
                } else {
                    // Can't fit above either, position at top of viewport
                    top = viewportTop + 10;
                }
            }
            
            tooltip.style.left = left + 'px';
            tooltip.style.top = top + 'px';
        }
        
        function hideCompanyTooltip() {
            // Add a small delay to prevent flickering when quickly moving between elements
            tooltipTimeout = setTimeout(() => {
                const tooltip = document.getElementById('companyTooltip');
                if (tooltip) {
                    tooltip.style.display = 'none';
                }
            }, 100);
        }
        
        // Initialize sortable tables when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            var tables = document.querySelectorAll('table.sortable');
            tables.forEach(makeSortable);
        });
    </script>
</body>
</html>'''
        
        return html

    def save_html_report(self, filename="index.html"):
        """Save the HTML report to a file"""
        html_content = self.generate_html_report()
        
        output_path = os.path.join(os.path.dirname(__file__), filename)
        import codecs
        with codecs.open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print("HTML report generated: {}".format(output_path))
        return output_path

    def save_raw_data(self, filename="company_data_v6.json"):
        """Save raw company data as JSON for analysis"""
        output_path = os.path.join(os.path.dirname(__file__), filename)
        import codecs
        with codecs.open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.companies, f, indent=2, ensure_ascii=False)
            
        print("Raw data saved: {}".format(output_path))
        return output_path

if __name__ == "__main__":
    try:
        parser = Victoria3CompanyParserV6Final("game")
        
        # Try to load existing data first, fall back to parsing if needed
        try:
            import json
            with open('company_data.json', 'r') as f:
                parser.companies = json.load(f)
            
            # Rebuild all_buildings set from loaded data
            parser.all_buildings = set()
            for company_data in parser.companies.values():
                parser.all_buildings.update(company_data['building_types'])
                parser.all_buildings.update(company_data['extension_building_types'])
            
            print("Loaded {} companies with {} unique buildings from existing data".format(len(parser.companies), len(parser.all_buildings)))
            
            # Load prestige goods mapping (needed for HTML generation)
            parser.prestige_goods = {
                'prestige_good_ford_automobiles': 'automobiles',
                'prestige_good_turin_automobiles': 'automobiles',
                'prestige_good_schichau_engines': 'engines',
                'prestige_good_krupp_guns': 'artillery',
                'prestige_good_schneider_guns': 'artillery',
                'prestige_good_armstrong_ships': 'clipper_transports',
                'prestige_good_colt_revolvers': 'small_arms',
                'prestige_good_saint_etienne_rifles': 'small_arms',
                'prestige_good_bohemian_crystal': 'glass',
                'prestige_good_meissen_porcelain': 'porcelain',
                'prestige_good_bentwood_furniture': 'furniture',
                'prestige_good_stylish_furniture': 'luxury_furniture',
                'prestige_good_english_upholstery': 'luxury_furniture',
                'prestige_good_designer_clothes': 'luxury_clothes',
                'prestige_good_haute_couture': 'luxury_clothes',
                'prestige_good_como_silk': 'silk',
                'prestige_good_suzhou_silk': 'silk',
                'prestige_good_tomioka_silk': 'silk',
                'prestige_good_sea_island_cotton': 'fabric',
                'prestige_good_craft_paper': 'paper',
                'prestige_good_washi_paper': 'paper',
                'prestige_good_precision_tools': 'tools',
                'prestige_good_refined_steel': 'steel',
                'prestige_good_sheffield_steel': 'steel',
                'prestige_good_russia_iron': 'iron',
                'prestige_good_oregrounds_iron': 'iron',
                'prestige_good_swedish_bar_iron': 'iron',
                'prestige_good_baku_oil': 'oil',
                'prestige_good_sicilian_sulfur': 'sulfur',
                'prestige_good_rosewood': 'hardwood',
                'prestige_good_burmese_teak': 'hardwood',
                'prestige_good_teak': 'hardwood',
                'prestige_good_prime_meat': 'meat',
                'prestige_good_river_plate_beef': 'meat',
                'prestige_good_select_fish': 'fish',
                'prestige_good_gourmet_groceries': 'groceries',
                'prestige_good_generic_groceries': 'groceries',
                'prestige_good_fine_grain': 'grain',
                'prestige_good_reserve_coffee': 'coffee',
                'prestige_good_china_tea': 'tea',
                'prestige_good_assam_tea': 'tea',
                'prestige_good_mit_afifi': 'tobacco',
                'prestige_good_turkish_tobacco': 'tobacco',
                'prestige_good_champagne': 'wine',
                'prestige_good_gros_michel_banana': 'fruit',
                'prestige_good_pure_opium': 'opium',
                'prestige_good_bengal_opium': 'opium',
                'prestige_good_smirnoff_vodka': 'liquor',
                'prestige_good_swift_merchant_marine': 'clipper_transports',
                'prestige_good_clyde_built_liners': 'steamers',
                'prestige_good_high_grade_explosives': 'explosives',
                'prestige_good_enriched_fertilizer': 'fertilizer',
                'prestige_good_german_aniline': 'dye',
                'prestige_good_high_powered_small_arms': 'small_arms',
                'prestige_good_quick_fire_artillery': 'artillery',
                'prestige_good_satsuma_ware': 'porcelain',
                'prestige_good_radiola_radios': 'radios',
                'prestige_good_chapel_radios': 'radios',
                'prestige_good_ericsson_apparatus': 'telephones'
            }
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print("Could not load existing data ({}), parsing from game files...".format(e))
            parser.cross_check_with_wiki()
            parser.save_raw_data()
        
        parser.save_html_report()
        
    except Exception as e:
        print("Error: {}".format(e))