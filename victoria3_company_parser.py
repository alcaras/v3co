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
        self.setup_country_names()
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
        
    def setup_country_names(self):
        """Map country codes to display names"""
        self.country_names = {
            'USA': 'United States', 'GBR': 'Great Britain', 'FRA': 'France', 'DEU': 'Germany',
            'PRU': 'Prussia', 'AUS': 'Austria-Hungary', 'RUS': 'Russia', 'JAP': 'Japan',
            'CHI': 'China', 'ITA': 'Italy', 'SAR': 'Sardinia-Piedmont', 'SPA': 'Spain',
            'POR': 'Portugal', 'NET': 'Netherlands', 'BEL': 'Belgium', 'SWI': 'Switzerland',
            'DEN': 'Denmark', 'SWE': 'Sweden', 'NOR': 'Norway', 'FIN': 'Finland',
            'ARG': 'Argentina', 'BRZ': 'Brazil', 'CHL': 'Chile', 'BOL': 'Bolivia', 'PEU': 'Peru',
            'COL': 'Colombia', 'CLM': 'Colombia', 'VNZ': 'Venezuela', 'ECU': 'Ecuador', 'URU': 'Uruguay', 'PRG': 'Paraguay',
            'MEX': 'Mexico', 'CUB': 'Cuba', 'HAI': 'Haiti', 'CAN': 'Canada', 'TUR': 'Turkey',
            'EGY': 'Egypt', 'PER': 'Persia', 'AFG': 'Afghanistan', 'ETH': 'Ethiopia', 'MAD': 'Madagascar',
            'SAF': 'South Africa', 'MOR': 'Morocco', 'TUN': 'Tunisia', 'GRE': 'Greece', 'SER': 'Serbia',
            'BUL': 'Bulgaria', 'ROM': 'Romania', 'HUN': 'Hungary', 'POL': 'Poland',
            'KOR': 'Korea', 'SIA': 'Siam', 'BUR': 'Burma', 'BIC': 'British India', 'AST': 'Australia',
            'PHI': 'Philippines', 'DAI': 'Vietnam', 'LAN': 'Lanfang', 'KOK': 'Turkestan', 'SOK': 'Niger'
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
    
    def format_prosperity_bonuses(self, bonuses):
        """Format prosperity bonuses for inline display"""
        if not bonuses:
            return ""
        
        # Join all bonuses with commas, clean up formatting
        formatted_bonuses = []
        for bonus in bonuses:
            # Clean up the bonus text - remove extra spaces, underscores
            clean_bonus = bonus.replace('_', ' ').strip()
            # Remove redundant 'add = ' and 'mult =' text for cleaner display
            clean_bonus = clean_bonus.replace(' add = ', ' +').replace(' mult = ', ' ×')
            formatted_bonuses.append(clean_bonus)
        
        return " -- " + "; ".join(formatted_bonuses)
    
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
        # Building display name overrides (for UI display)
        building_display_name_overrides = {
            'building_chemical_plants': 'Fertilizer Plants'
        }
        
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
            'prosperity_bonuses': [],
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
                                
                                # Detect special requirement types for filtering
                                special_requirements = []
                                
                                # Check for journal entry requirements (in both potential and possible sections)
                                all_content = potential_content + ' ' + possible_content
                                if ('journal_entry' in all_content.lower() or 
                                    'complete_journal' in all_content.lower() or
                                    'is_meiji_japan' in all_content or
                                    'meiji_restoration' in all_content.lower()):
                                    special_requirements.append('journal_entry')
                                    
                                # Check for primary culture requirements (country-specific)
                                if 'country_has_primary_culture' in potential_content:
                                    special_requirements.append('primary_culture')
                                    
                                # Check for specific technology requirements
                                if 'has_technology' in potential_content:
                                    special_requirements.append('technology')
                                    
                                # Check for law requirements
                                if 'has_law' in potential_content:
                                    special_requirements.append('law')
                                    
                                # Check for ideology requirements
                                if 'ruler_ideology' in potential_content or 'government_ideology' in potential_content:
                                    special_requirements.append('ideology')
                                    
                                # Check for war or diplomatic status requirements
                                if 'at_war' in potential_content or 'in_diplomatic_play' in potential_content:
                                    special_requirements.append('diplomatic')
                                    
                                # Check for regional requirements
                                if ('has_interest_marker_in_region' in potential_content or 
                                    'region_' in potential_content or
                                    'in_region' in potential_content):
                                    special_requirements.append('regional')
                                    
                                company_data['special_requirements'] = special_requirements
                    else:
                        # No potential block found - this is a basic company
                        company_data['special_requirements'] = []
                    
                    company_data['formation_requirements'] = formation_reqs
                    
                    # Check if company starts enacted (from wiki data) 
                    company_data['starts_enacted'] = False
                    if hasattr(self, 'wiki_companies'):
                        company_clean_name = company_name.replace('company_', '')
                        wiki_entry = self.wiki_companies.get(company_clean_name, {})
                        wiki_text = wiki_entry.get('text', '')
                        if 'starts with this company established' in wiki_text.lower():
                            company_data['starts_enacted'] = True
                    
                    # Additional check: hardcode known pre-enacted companies from wiki
                    pre_enacted_companies = {
                        'hbc', 'massey_harris', 'william_cramp', 
                        'east_india_company', 'john_cockerill', 'confédération_générale_des_vignerons',
                        'rheinmetall', 'russian_american_company'
                    }
                    if company_clean_name in pre_enacted_companies:
                        company_data['starts_enacted'] = True
                        
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
                    
                    # Extract journal entry requirements
                    if ('journal_entry' in company_data.get('special_requirements', []) or
                        'has_journal_entry' in possible_content or
                        'complete_journal' in possible_content.lower() or
                        'is_meiji_japan' in possible_content or
                        'meiji_restoration' in possible_content.lower()):
                        company_data['formation_requirements'].append("Journal Entry Required")
                    
                    # Extract pre-enacted status
                    if company_data.get('starts_enacted', False):
                        company_data['formation_requirements'].append("Starts Enacted at Game Start")
        
        # Parse prosperity bonuses from prosperity_modifier - show raw content
        prosperity_match = re.search(r'prosperity_modifier\s*=\s*\{([^{}]+)\}', company_content)
        if prosperity_match:
            prosperity_content = prosperity_match.group(1).strip()
            # Clean up the raw content for display
            bonuses = []
            for line in prosperity_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    # Clean up the line for display
                    clean_line = line.replace('_', ' ').replace('\t', ' ')
                    clean_line = ' '.join(clean_line.split())  # Remove extra whitespace
                    bonuses.append(clean_line)
            
            company_data['prosperity_bonuses'] = bonuses
        
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
    
    def get_building_display_name(self, building_name):
        """Get the display name for a building, with special case overrides"""
        # Building display name overrides (for UI display)
        building_display_name_overrides = {
            'building_chemical_plants': 'Fertilizer Plants'
        }
        
        if building_name in building_display_name_overrides:
            return building_display_name_overrides[building_name]
        else:
            return building_name.replace('building_', '').replace('_', ' ').title()
    
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
    
    def get_countries_by_continent(self):
        """Get countries organized by continent following wiki structure"""
        continents = {
            'American': {
                'display_name': 'Americas', 
                'countries': ['ARG', 'BOL', 'BRZ', 'CAN', 'CLM', 'CHL', 'MEX', 'PRG', 'PEU', 'USA', 'VNZ']
            },
            'Asian_Oceanian': {
                'display_name': 'Asia & Oceania',
                'countries': ['AST', 'CHI', 'BIC', 'JAP', 'KOR', 'LAN', 'PHI', 'SIA', 'DAI']
            },
            'European': {
                'display_name': 'Europe', 
                'countries': ['AUS', 'BEL', 'DEN', 'FIN', 'FRA', 'DEU', 'GBR', 'GRE', 'ITA', 'NET', 'NOR', 'POL', 'POR', 'ROM', 'RUS', 'SER', 'SPA', 'SWE']
            },
            'Middle_Eastern': {
                'display_name': 'Middle East & Africa',
                'countries': ['AFG', 'EGY', 'PER', 'KOK', 'TUR', 'ETH', 'SOK', 'SAF']
            }
        }
        
        # Count companies per country
        country_counts = {}
        for company_name, data in self.companies.items():
            country = data.get('country')
            if country and not company_name.startswith('company_basic_'):
                country_counts[country] = country_counts.get(country, 0) + 1
        
        # Filter continents to only include countries with companies
        filtered_continents = {}
        for continent_key, continent_data in continents.items():
            countries_with_companies = []
            for country in continent_data['countries']:
                if country in country_counts:
                    countries_with_companies.append({
                        'code': country,
                        'count': country_counts[country]
                    })
            
            if countries_with_companies:
                filtered_continents[continent_key] = {
                    'display_name': continent_data['display_name'],
                    'countries': sorted(countries_with_companies, key=lambda x: x['code'])
                }
        
        return filtered_continents
    
    def _generate_country_filter_section(self, countries_by_continent):
        """Generate HTML for hierarchical country/company filter section"""
        if not countries_by_continent:
            return ""
            
        html = '''
    
    <div class="toc">
        <a name="countries"></a>
        <h3 id="countries">Countries and Companies</h3>
        <div class="building-filter-help" style="margin-bottom: 15px; padding: 10px; background: #fff3e0; border: 1px solid #ff9800; border-radius: 4px; font-size: 13px;">
            <strong>Company Filter:</strong> Enable/disable specific companies or entire countries. Disabled companies are excluded from optimization and tables.
            <div style="margin-top: 8px; display: flex; align-items: center; justify-content: space-between;">
                <div class="quick-actions" style="display: flex; flex-wrap: wrap; gap: 5px;">
                    <strong style="font-size: 11px;">Quick Actions:</strong>
                    <button onclick="toggleAllCompanyFilters(true)" class="control-btn" style="font-size: 11px; padding: 2px 6px; background-color: #28a745; color: white;">✓ Enable All</button>
                    <button onclick="toggleAllCompanyFilters(false)" class="control-btn" style="font-size: 11px; padding: 2px 6px; background-color: #6c757d; color: white;">🗑 Clear All</button>
                    <button onclick="toggleCompanyCategory('basic_only', true)" class="control-btn" style="font-size: 11px; padding: 2px 6px; background-color: #17a2b8; color: white;">⭐ Basic Only</button>
                    <button onclick="toggleCompanyCategory('pre_enacted', false)" class="control-btn" style="font-size: 11px; padding: 2px 6px; background-color: #ffc107; color: black;">🚫 No Game Start</button>
                    <button onclick="toggleCompanyCategory('culture_restricted', false)" class="control-btn" style="font-size: 11px; padding: 2px 6px; background-color: #dc3545; color: white;">🚫 No Culture Req</button>
                    <button onclick="toggleCompanyCategory('journal_required', false)" class="control-btn" style="font-size: 11px; padding: 2px 6px; background-color: #fd7e14; color: white;">🚫 No Journal Req</button>
                </div>
                <div class="presets-container" style="display: flex; align-items: center; gap: 5px; margin-top: 5px;">
                    <strong style="font-size: 11px;">Presets:</strong>
                    <button onclick="exportCompanyPreset()" class="control-btn" style="font-size: 11px; padding: 2px 6px; background-color: #007bff; color: white;">📤 Export</button>
                    <button onclick="document.getElementById('preset-import').click()" class="control-btn" style="font-size: 11px; padding: 2px 6px; background-color: #28a745; color: white;">📥 Import</button>
                    <input type="file" id="preset-import" accept=".json" style="display: none;" onchange="importCompanyPreset(this)">
                </div>
            </div>
        </div>
        <div class="toc-columns">'''
        
        # Add basic companies section first
        basic_companies = []
        for company_key, company_data in self.companies.items():
            if company_key.startswith('company_basic_'):
                company_name = company_data.get('display_name', company_key.replace('company_', '').replace('_', ' ').title())
                
                # Create tooltip
                buildings = company_data.get('building_types', [])
                charters = company_data.get('extension_building_types', [])
                tooltip_parts = []
                
                if buildings:
                    building_names = [b.replace('building_', '').replace('_', ' ').title() for b in buildings]
                    tooltip_parts.append(f"Buildings: {', '.join(building_names)}")
                
                if charters:
                    charter_names = [c.replace('building_', '').replace('_', ' ').title() for c in charters]
                    tooltip_parts.append(f"Charters: {', '.join(charter_names)}")
                    
                tooltip = ' | '.join(tooltip_parts)
                
                # Get company icon
                clean_name = company_key.replace('company_', '')
                icon_path = self.get_company_icon_path(clean_name)
                icon_display = f'<img src="{icon_path}" class="company-icon" alt="Company Icon" style="width: 16px; height: 16px; margin-right: 4px;">' if icon_path else ''
                
                basic_companies.append({
                    'key': company_key,
                    'name': company_name,
                    'tooltip': tooltip,
                    'icon': icon_display
                })
        
        if basic_companies:
            html += '''
            <div style="margin-bottom: 20px;">
                <div style="background: #f8f9fa; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; margin-bottom: 10px;">
                    <div style="display: flex; align-items: center;">
                        <input type="checkbox" id="all-basic-companies" class="basic-companies-checkbox" checked onchange="toggleAllBasicCompanies(this)" style="margin-right: 8px;">
                        <h4 style="margin: 0; font-size: 14px; color: #495057;">Basic Companies</h4>
                    </div>
                </div>'''
            
            for company in basic_companies:
                html += '''
                <div class="company-selection-item" style="margin: 3px 0; padding: 2px 20px; display: flex; align-items: center; font-size: 13px; position: relative;">
                    <input type="checkbox" id="company-{}" class="company-checkbox" checked data-company="{}" data-country="basic" onchange="updateCompanyFilter(this)" style="margin-right: 8px;">
                    <span title="{}" style="display: flex; align-items: center; cursor: pointer;" 
                          onmouseover="showCompanyTooltip(event, '{}')" 
                          onmouseout="hideCompanyTooltip()">{}{}</span>
                </div>'''.format(
                company['key'], company['key'], company['tooltip'], company['key'], company['icon'], company['name']
            )
            
            # Add Mandate Companies section within the same container
            construction_company = self.companies.get('company_construction_power_bloc')
            if construction_company:
                html += '''
                <div style="background: #fff3cd; padding: 8px 12px; border: 1px solid #ffeaa7; border-radius: 4px; margin-bottom: 10px;">
                    <h4 style="margin: 0; font-size: 14px; color: #856404;">Mandate Companies</h4>
                </div>
                <div class="company-selection-item" style="margin: 3px 0; padding: 2px 20px; display: flex; align-items: center; font-size: 13px; position: relative;">
                    <input type="checkbox" id="company-company_construction_power_bloc" class="company-checkbox" checked data-company="company_construction_power_bloc" data-country="mandate" onchange="updateCompanyFilter(this)" style="margin-right: 8px;">
                    <span style="display: flex; align-items: center; cursor: pointer;" 
                          onmouseover="showCompanyTooltip(event, 'company_construction_power_bloc')" 
                          onmouseout="hideCompanyTooltip()">United Construction Conglomerate</span>
                </div>
                '''
            
            html += '''
            </div>'''
        
        # Build companies by country first
        companies_by_country = {}
        for company_key, company_data in self.companies.items():
            country = company_data.get('country', 'unknown')
            if country == 'unknown' or country not in [info['code'] for continent in countries_by_continent.values() for info in continent['countries']]:
                continue  # Skip companies without valid countries
                
            if country not in companies_by_country:
                companies_by_country[country] = []
            
            # Get company display name and categorize
            company_name = company_data.get('display_name', company_key.replace('company_', '').replace('_', ' ').title())
            special_reqs = company_data.get('special_requirements', [])
            starts_enacted = company_data.get('starts_enacted', False)
            
            # Create tooltip with company details
            buildings = company_data.get('building_types', [])
            charters = company_data.get('extension_building_types', [])
            tooltip_parts = []
            
            if buildings:
                building_names = [b.replace('building_', '').replace('_', ' ').title() for b in buildings]
                tooltip_parts.append(f"Buildings: {', '.join(building_names)}")
            
            if charters:
                charter_names = [c.replace('building_', '').replace('_', ' ').title() for c in charters]
                tooltip_parts.append(f"Charters: {', '.join(charter_names)}")
                
            if starts_enacted:
                tooltip_parts.append("⚠️ Starts enacted at game start")
                
            # Categorize special requirements for different icons
            has_culture_req = 'primary_culture' in special_reqs
            has_journal_req = 'journal_entry' in special_reqs
            has_tech_req = 'technology' in special_reqs
            has_other_restrictive = any(req in special_reqs for req in ['law', 'ideology', 'diplomatic'])
            
            if special_reqs:
                req_names = {
                    'primary_culture': 'Primary Culture Required',
                    'journal_entry': 'Journal Entry Required', 
                    'technology': 'Technology Required',
                    'law': 'Law Required',
                    'ideology': 'Ideology Required',
                    'diplomatic': 'Diplomatic Status Required',
                    'regional': 'Regional Interest Required'
                }
                req_details = [req_names.get(req, req.title()) for req in special_reqs]
                
                # Use specific icons for different requirement types
                if has_culture_req and has_journal_req:
                    tooltip_parts.append(f"🛑📚 Special: {', '.join(req_details)}")
                elif has_culture_req:
                    tooltip_parts.append(f"🛑 Primary Culture Required")
                elif has_journal_req:
                    tooltip_parts.append(f"📚 Journal Entry Required")
                elif has_tech_req:
                    tooltip_parts.append(f"Technology Required")
                elif has_other_restrictive:
                    tooltip_parts.append(f"🔒 Special: {', '.join(req_details)}")
                elif len(special_reqs) == 1 and 'regional' in special_reqs:
                    # Don't show icon for regional-only requirements (too common)
                    tooltip_parts.append(f"Regional Interest Required")
                else:
                    # Show other requirements without prominent icon
                    tooltip_parts.append(f"Special: {', '.join(req_details)}")
            
            tooltip = ' | '.join(tooltip_parts)
                
            companies_by_country[country].append({
                'key': company_key,
                'name': company_name,
                'special_reqs': special_reqs,
                'has_culture_req': has_culture_req,
                'has_journal_req': has_journal_req,
                'has_tech_req': has_tech_req,
                'has_other_restrictive': has_other_restrictive,
                'starts_enacted': starts_enacted,
                'tooltip': tooltip,
                'buildings_count': len(buildings) + len(charters)
            })
        
        # Sort companies within each country by name
        for country in companies_by_country:
            companies_by_country[country].sort(key=lambda x: x['name'])
        
        # Generate HTML by continent
        for continent_key, continent_data in countries_by_continent.items():
            html += '''<div style="flex: 1; min-width: 0;">
                <h4 style="display: flex; align-items: center; margin-bottom: 10px;">
                    <input type="checkbox" id="continent-{}" class="continent-checkbox" checked data-continent="{}" onchange="toggleAllCompaniesInContinent(this)" style="margin-right: 8px;">
                    {}
                </h4>'''.format(continent_key, continent_key, continent_data['display_name'])
            
            for country_info in continent_data['countries']:
                country_code = country_info['code']
                companies = companies_by_country.get(country_code, [])
                
                if not companies:  # Skip countries with no companies
                    continue
                    
                # Get country display name and flag
                country_name = self.country_names.get(country_code, country_code)
                flag_icon = self.country_flags.get(country_code, '🏳️')
                
                # Simple country header with checkbox - indented under continent
                html += '''
                <div class="country-section" style="margin-bottom: 15px; margin-left: 20px;">
                    <div class="country-header" style="padding: 4px 0; font-weight: bold; border-bottom: 1px solid #ddd;">
                        <input type="checkbox" id="country-{}" class="country-checkbox" checked data-country="{}" onchange="toggleAllCompaniesInCountry(this)" style="margin-right: 8px;">
                        <span title="{}">{}</span> {} ({})
                    </div>'''.format(
                    country_code, country_code, country_name, flag_icon, country_name, len(companies)
                )
                
                # List all companies for this country with simple indented checkboxes  
                for company in companies:
                    # Get company icon or use default
                    company_icon = self.get_company_icon_path(company['key'])
                    icon_display = f'<img src="{company_icon}" style="width: 16px; height: 16px; margin-right: 6px; vertical-align: middle;">' if company_icon != 'default_icon.png' else '🏢 '
                    
                    # Add special requirement indicators with specific icons
                    indicators = []
                    if company['starts_enacted']:
                        indicators.append('⚠️')
                    
                    # Use specific requirement icons
                    if company['has_culture_req'] and company['has_journal_req']:
                        indicators.append('🛑📚')
                    elif company['has_culture_req']:
                        indicators.append('🛑')
                    elif company['has_journal_req']:
                        indicators.append('📚')
                    elif company['has_tech_req']:
                        pass  # No icon for tech requirements
                    elif company['has_other_restrictive']:
                        indicators.append('🔒')
                    # Don't show any icon for regional-only requirements (77% of companies have this)
                    
                    indicator_text = ''.join(indicators) + (' ' if indicators else '')
                    
                    html += '''
                        <div class="company-selection-item" style="margin: 3px 0; padding: 2px 20px; display: flex; align-items: center; font-size: 13px; position: relative;">
                            <input type="checkbox" id="company-{}" class="company-checkbox" checked data-company="{}" data-country="{}" onchange="updateCompanyFilter(this)" style="margin-right: 8px;">
                            <span title="{}" style="display: flex; align-items: center; cursor: pointer;" 
                                  onmouseover="showCompanyTooltip(event, '{}')" 
                                  onmouseout="hideCompanyTooltip()">{}{}{}</span>
                        </div>'''.format(
                        company['key'], company['key'], country_code,
                        company['tooltip'], company['key'], icon_display, indicator_text, company['name']
                    )
                
                html += '''
                </div>'''
            
            html += '</div>'
        
        html += '''
        </div>
    </div>'''
        
        return html

    def _generate_company_id_mappings(self):
        """Generate JavaScript object mapping company keys to sequential IDs"""
        companies = sorted(self.companies.keys())
        mappings = []
        for i, company_key in enumerate(companies):
            mappings.append(f"'{company_key}': {i}")
        return ',\n            '.join(mappings)
    
    def _generate_building_id_mappings(self):
        """Generate JavaScript object mapping building keys to sequential IDs"""
        # Use all buildings from companies data, sorted for consistent ordering
        all_buildings = set()
        for company in self.companies.values():
            all_buildings.update(company.get('building_types', []))
            all_buildings.update(company.get('extension_building_types', []))
        
        buildings = sorted(all_buildings)
        mappings = []
        for i, building_key in enumerate(buildings):
            mappings.append(f"'{building_key}': {i}")
        return ',\n            '.join(mappings)
    
    def generate_html_report(self):
        """Generate HTML analysis report with all bugs fixed"""
        
        # Include the working YALPS bundle  
        try:
            with open('yalps-browserify-direct.js', 'r') as f:
                yalps_bundle = f.read()
        except:
            yalps_bundle = "// YALPS bundle not found"
        
        # Get building frequencies and order buildings logically based on Victoria 3 wiki
        building_counts = self.get_building_frequency(self.companies)
        
        # Get country data organized by continent
        countries_by_continent = self.get_countries_by_continent()
        
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
        
        # Generate CSS rules for column hiding and country hiding
        column_hiding_css = self._generate_column_hiding_css(buildings_to_analyze)
        country_hiding_css = self._generate_country_hiding_css(countries_by_continent)
        
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
        
        /* Specific styling for custom companies table to prevent stretching */
        #custom-companies-table .table-container {
            width: fit-content;
            max-width: none;
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
            padding: 0px !important;
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
        
        /* Ensure dynamic coverage column header has brown background like other headers */
        .building-table th.dynamic-coverage-column {
            background-color: #d2b48c !important;
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
        
        /* Custom Company Collection Styling */
        #custom-companies-section {
            background: #f0ead6;
            border: 2px solid #8b6914;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        #custom-companies-section h2 {
            margin-top: 0;
            color: #8b4513;
            text-align: center;
        }
        
        .add-to-custom-btn {
            background: #4a7c59;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }
        
        .add-to-custom-btn:hover:not(:disabled) {
            background: #5a8c69;
        }
        
        .add-to-custom-btn:disabled {
            background: #6c7b5e;
            cursor: not-allowed;
        }
        
        .remove-btn {
            background: #c85450;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        
        .remove-btn:hover {
            background: #d86460;
        }
        
        .select-column {
            width: 20px;
            text-align: center;
            padding: 0px !important;
        }
        
        .company-checkbox {
            transform: scale(1.2);
            cursor: pointer;
        }
        
        /* Charter Selection Styling */
        .clickable-charter {
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .clickable-charter:hover {
            background-color: #fff3cd !important;
        }
        
        .selected-charter {
            background-color: #ffd700 !important;
            color: #000 !important;
            font-weight: bold;
        }
        
        .dimmed-charter {
            opacity: 0.4;
            color: #999 !important;
        }
        
        /* Drag and Drop Styling - only for draggable cells */
        #custom-companies-table td[draggable="true"] {
            cursor: grab;
        }
        
        #custom-companies-table td[draggable="true"]:active {
            cursor: grabbing;
        }
        
        #custom-companies-table td[draggable="true"]:hover {
            background-color: #f5f5f5;
        }
        
        /* Selection Control Buttons */
        .control-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: background-color 0.2s;
        }
        
        .import-export-buttons .control-btn {
            margin: 0 4px;
        }
        
        .import-export-buttons .control-btn:first-child {
            margin-left: 0;
        }
        
        .import-export-buttons .control-btn:last-child {
            margin-right: 0;
        }
        
        .clear-btn {
            background-color: #dc3545;
            color: white;
        }
        
        /* Optimization Modal */
        .optimization-modal {
            display: none;
            position: fixed;
            z-index: 10000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        
        .optimization-modal-content {
            background-color: #fefefe;
            margin: 5% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 80%;
            max-width: 800px;
            border-radius: 8px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .optimization-results {
            margin-top: 20px;
        }
        
        .optimization-company-item {
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #f9f9f9;
        }
        
        .optimization-company-new {
            background: #e8f5e9;
            border-color: #4caf50;
        }
        
        .optimization-company-existing {
            background: #f3f4f6;
            border-color: #9ca3af;
        }
        
        .optimization-stats {
            display: flex;
            gap: 20px;
            margin: 20px 0;
            padding: 15px;
            background: #f0f0f0;
            border-radius: 4px;
        }
        
        .optimization-stat {
            flex: 1;
            text-align: center;
        }
        
        .optimization-stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .optimization-stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        .clear-btn:hover:not(:disabled) {
            background-color: #c82333;
        }
        
        .control-btn:disabled {
            background-color: #6c757d !important;
            color: #fff !important;
            cursor: not-allowed;
            opacity: 0.6;
        }
        
        .save-btn {
            background-color: #28a745;
            color: white;
        }
        
        .save-btn:hover:not(:disabled) {
            background-color: #218838;
        }
        
        .import-btn {
            background-color: #007bff;
            color: white;
        }
        
        .import-btn:hover {
            background-color: #0056b3;
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
            width: 24px !important;
            min-width: 24px !important;
            max-width: 24px !important;
            text-align: center !important;
            font-size: 14px !important;
            padding: 0px !important;
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
            width: 28px !important;
            min-width: 28px !important;
            max-width: 28px !important;
            text-align: center !important;
            padding: 0px !important;
            font-size: 12px !important;
            overflow: hidden !important;
            white-space: nowrap !important;
        }

        table.building-table th.dynamic-coverage-column,
        table.building-table td.dynamic-coverage-column,
        .building-table th.dynamic-coverage-column,
        .building-table td.dynamic-coverage-column,
        th.dynamic-coverage-column,
        td.dynamic-coverage-column {
            width: 28px !important;
            min-width: 28px !important;
            max-width: 28px !important;
            text-align: center !important;
            padding: 0px !important;
            font-size: 12px !important;
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
        
        .prosperity-bonuses {
            font-size: 11px;
            color: #666;
            margin-top: 2px;
            line-height: 1.2;
            font-style: italic;
        }
        
        /* Removed duplicate header rule - handled above */
        
        /* Removed duplicate table rules - handled above with aggressive selectors */
        
        /* Building columns - ABSOLUTE FIXED WIDTH */
        table.building-table th:not(.flag-column):not(.dynamic-coverage-column):not(.buildings-column):not(.company-name),
        table.building-table td:not(.flag-column):not(.dynamic-coverage-column):not(.buildings-column):not(.company-name),
        .building-table th:not(.flag-column):not(.dynamic-coverage-column):not(.buildings-column):not(.company-name),
        .building-table td:not(.flag-column):not(.dynamic-coverage-column):not(.buildings-column):not(.company-name) {
            width: 36px !important;
            min-width: 36px !important;
            max-width: 36px !important;
            text-align: center !important;
            padding: 0px !important;
            overflow: hidden !important;
            white-space: nowrap !important;
        }
        
        /* Removed duplicate company name rules - handled above */
        
        .company-name:hover {
            /* Remove underline to avoid link-like appearance */
        }
        
        .building-header {
            width: 36px;
            min-width: 36px;
            max-width: 36px;
            height: 36px;
            background-size: 32px 32px;
            background-repeat: no-repeat;
            background-position: center;
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            position: relative;
            padding: 0px !important;
            margin: 0px !important;
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
        
        /* Green checkbox overlay for covered buildings - show everywhere EXCEPT Selected Companies table */
        .building-header.covered::after {
            content: "✓";
            position: absolute;
            bottom: 2px;
            right: 2px;
            width: 12px;
            height: 12px;
            background-color: #4CAF50;
            color: white;
            border-radius: 2px;
            font-size: 10px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 1px 2px rgba(0,0,0,0.3);
            z-index: 10;
        }
        
        /* Hide green checkboxes specifically in Selected Companies table */
        #custom-companies-table .building-header.covered::after {
            display: none;
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
        
        /* Multi-column flexbox layout for filters */
        .toc-columns {
            display: flex;
            gap: 15px;
            align-items: flex-start;
            justify-content: space-between;
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
            display: flex;
            align-items: center;
        }
        
        .category-item .building-filter-checkbox {
            margin-right: 6px;
            margin-top: 0;
            flex-shrink: 0;
        }
        
        .category-item a {
            font-size: 13px;
            display: flex;
            align-items: center;
            flex: 1;
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
        
        /* Dynamic column hiding rules for building filters */
        __COLUMN_HIDING_CSS_PLACEHOLDER__
        
        /* Responsive Design - Mobile First Approach */
        @media (max-width: 768px) {
            /* General mobile layout fixes */
            body {
                padding: 10px 5px;
            }
            
            /* Fix header buttons and dropdowns */
            .control-btn {
                padding: 6px 10px !important;
                font-size: 12px !important;
                margin: 2px !important;
            }
            
            /* CRITICAL FIX: Target ALL company/country items with inline styles */
            div[style*="display: flex"][style*="align-items: center"] input[type="checkbox"].company-checkbox {
                position: relative !important;
                margin-right: 12px !important;
                width: 20px !important;
                height: 20px !important;
                flex-shrink: 0 !important;
            }
            
            /* Fix all spans that follow checkboxes */
            .company-checkbox + span {
                display: inline-block !important;
                word-wrap: break-word !important;
                max-width: calc(100% - 40px) !important;
            }
            
            /* Fix overlapping text in company selection */
            .company-selection-item {
                padding: 8px 5px !important;
                min-height: 40px !important;
                position: relative !important;
                display: block !important;
                margin: 5px 0 !important;
            }
            
            .company-selection-item > input[type="checkbox"] {
                position: absolute !important;
                left: 5px !important;
                top: 12px !important;
                transform: scale(1.2) !important;
                margin: 0 !important;
                width: 20px !important;
                height: 20px !important;
            }
            
            .company-selection-item > span {
                margin-left: 35px !important;
                display: block !important;
                line-height: 1.5 !important;
                padding-right: 5px !important;
            }
            
            /* Override inline flex styles */
            .company-selection-item[style*="display: flex"] {
                display: block !important;
            }
            
            /* Fix checkbox alignment in all company items */
            .company-checkbox {
                flex-shrink: 0 !important;
                margin-right: 10px !important;
            }
            
            /* Fix country sections */
            .country-section {
                margin-left: 10px !important;
            }
            
            .country-header {
                display: flex !important;
                align-items: center !important;
                padding: 8px 0 !important;
                position: relative !important;
            }
            
            .country-header input[type="checkbox"] {
                flex-shrink: 0 !important;
                margin-right: 8px !important;
            }
            
            /* Fix continent sections */
            .continent-section h4 {
                display: flex !important;
                align-items: center !important;
                padding: 8px 0 !important;
                font-size: 15px !important;
            }
            
            .continent-section h4 input[type="checkbox"] {
                margin-right: 8px !important;
                flex-shrink: 0 !important;
            }
            
            /* Fix the TOC columns container */
            .toc-columns {
                display: block !important;
                padding: 5px !important;
            }
            
            /* Fix column widths on mobile */
            .toc-columns > div[style*="flex: 1"] {
                width: 100% !important;
                flex: none !important;
                margin-bottom: 15px !important;
            }
            
            /* Fix button groups */
            div[style*="display: flex"][style*="gap"] {
                flex-wrap: wrap !important;
            }
            
            /* Fix dropdown in header */
            #company-limit-dropdown {
                width: 100%;
                margin-top: 5px;
            }
            
            /* Fix optimize button */
            .optimize-btn {
                width: 100%;
                margin-bottom: 5px;
            }
            
            /* Fix preset buttons container */
            .presets-container {
                flex-direction: column !important;
                align-items: stretch !important;
                gap: 5px !important;
            }
            
            .presets-container button {
                width: 100% !important;
                margin: 2px 0 !important;
            }
            
            /* Fix legend layout */
            .legend-container {
                gap: 8px !important;
                font-size: 12px !important;
            }
            
            /* Fix table of contents columns */
            .toc-columns {
                display: block !important;
            }
            
            .toc-columns > div {
                width: 100% !important;
                margin-bottom: 20px;
            }
            
            /* Fix tables for mobile */
            table {
                font-size: 12px;
            }
            
            th, td {
                padding: 4px !important;
            }
            
            /* Hide less important columns on mobile */
            .dynamic-coverage-column {
                display: none;
            }
            
            /* Company tooltip adjustments */
            .company-tooltip {
                max-width: 90vw !important;
                font-size: 12px;
            }
            
            /* Charter selection mobile fixes */
            .charter-selection {
                padding: 10px !important;
            }
            
            /* Company filter sections */
            .filter-section {
                margin-bottom: 15px;
            }
            
            /* Quick actions buttons */
            .quick-actions {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            
            .quick-actions button {
                width: 100%;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .control-btn {
                padding: 8px 12px !important;
                font-size: 13px !important;
                width: 100%;
                margin: 3px 0 !important;
            }
            
            /* Stack all controls vertically */
            .header-controls {
                flex-direction: column !important;
            }
            
            /* Full width for all interactive elements */
            select, button {
                width: 100% !important;
            }
            
            /* Increase checkbox touch targets */
            input[type="checkbox"] {
                min-width: 20px;
                min-height: 20px;
            }
            
            /* Reduce font sizes for better fit */
            h3 {
                font-size: 18px;
            }
            
            h4 {
                font-size: 16px;
            }
            
            /* Company names and text */
            .company-name, .company-selection-item span {
                font-size: 13px;
            }
        }
    </style>
</head>
<body>
    <h1 id="top">Victoria 3 Company Analysis Tool</h1>
    
    <!-- Optimization Modal -->
    <div id="optimizationModal" class="optimization-modal">
        <div class="optimization-modal-content">
            <span onclick="closeOptimizationModal()" style="float: right; font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>
            <h2>Company Optimization Results</h2>
            <div id="optimizationStatus" style="margin: 10px 0; font-style: italic;"></div>
            <div id="optimizationResults"></div>
            <div style="margin-top: 20px; text-align: center;">
                <button onclick="applyOptimizationResults()" class="control-btn" style="background: #28a745; color: white; padding: 10px 20px; margin-right: 10px;">✅ Apply Selection</button>
                <button onclick="closeOptimizationModal()" class="control-btn" style="background: #6c757d; color: white; padding: 10px 20px;">Cancel</button>
            </div>
        </div>
    </div>
    
    <!-- Custom Company Collection Section -->
    <div id="custom-companies-section">
        <div class="selection-controls" style="margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; flex-wrap: nowrap;">
            <h2 id="selected-companies-title" style="margin: 0; flex-shrink: 0;">Selected Companies (0)</h2>
            <div class="header-controls" style="display: flex; align-items: center; flex-wrap: nowrap; gap: 8px;">
                <button onclick="optimizeSelection()" class="control-btn optimize-btn" style="background: #17a2b8; color: white; font-weight: bold; padding: 8px 16px;">🎯 Optimize</button>
                <select id="company-limit-dropdown" style="padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; min-width: 120px;">
                    <option value="7" selected>7 companies</option>
                    <option value="6">6 companies</option>
                    <option value="5">5 companies</option>
                    <option value="4">4 companies</option>
                </select>
                <button onclick="copyRedditMarkdown(event)" class="control-btn share-btn" style="background: #6f42c1; color: white; font-weight: bold; padding: 8px 16px;">📋 Share Build</button>
                <button onclick="saveSelection()" class="control-btn save-btn">💾 Export to JSON</button>
                <button onclick="triggerImportSelection()" class="control-btn import-btn">📂 Import from JSON</button>
                    <input type="file" id="import-file-input" accept=".json" onchange="importSelection(event)" style="display: none;">
                </div>
                <button onclick="clearSelection()" class="control-btn clear-btn">🗑️ Clear Selection</button>
            </div>
        </div>
        
        <!-- Tutorial text - shown when no companies selected -->
        <div id="tutorial-text" style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
            <p style="margin: 0 0 12px 0; color: #495057; font-weight: 500;">Getting Started:</p>
            <ul style="margin: 0; padding-left: 20px; color: #666; line-height: 1.6;">
                <li>Add companies from the tables below by checking the boxes</li>
                <li>Select industry charters by clicking charter cells: <span style="display: inline-flex; align-items: center; width: 16px; height: 16px; background: #FFF3E0; border: 1px solid #FF9800; border-radius: 2px; justify-content: center; font-size: 10px; margin: 0 2px;">○</span> (only available for selected companies)</li>
                <li>Use the ➕ column to see how many additional buildings each company would add to your selection</li>
                <li>Drag and drop companies to reorder them in your selection</li>
                <li>Deselecting a company automatically clears its charter selection</li>
                <li>Building count format: base buildings + charter options (e.g., 3.4 = 3 base buildings + 4 charter options, but you can only pick 1 charter per company)</li>
            </ul>
            
            <!-- Key/Legend moved here -->
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #dee2e6;">
                <p style="margin: 0 0 8px 0; color: #495057; font-weight: 500;">Key:</p>
                <div class="legend-container" style="display: flex; flex-wrap: wrap; gap: 16px; font-size: 14px; color: #666;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div class="prestige-building" style="width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; border-radius: 3px;"><img src="icons/24px-Prestige_ford_automobiles.png" width="16" height="16" alt="Prestige Good Example" title="Prestige Good"></div>
                        <span>Prestige Good</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 20px; height: 20px; background: #E3F2FD; border: 1px solid #2196F3; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 12px;">●</div>
                        <span>Base Building</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 20px; height: 20px; background: #FFF3E0; border: 1px solid #FF9800; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 12px;">○</div>
                        <span>Charter Available</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="custom-companies-table">
        </div>
    </div>
    
    <!-- Company tooltip -->
    <div id="companyTooltip" class="company-tooltip"></div>
    
    <div class="toc">
        <a name="buildings"></a>
        <h3 id="buildings">Buildings (<span id="selected-buildings-count">49</span>)</h3>
        <div class="building-filter-help" style="margin-bottom: 15px; padding: 10px; background: #f0f8ff; border: 1px solid #ccc; border-radius: 4px; font-size: 13px;">
            <strong>Building Filter:</strong> Use the checkboxes to show/hide building columns. Unchecked buildings are excluded from tables and dynamic calculations. All buildings start checked by default.
            <div style="margin-top: 8px; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <strong style="font-size: 11px;">Presets:</strong>
                    <button onclick="applyBuildingPreset('all_buildings')" class="control-btn" style="font-size: 11px; padding: 2px 6px; margin-left: 5px;">📋 All Buildings (49)</button>
                    <button onclick="applyBuildingPreset('key_economy')" class="control-btn" style="font-size: 11px; padding: 2px 6px; margin-left: 5px;">🏭 Key Economy (13)</button>
                    <button onclick="applyBuildingPreset('key_overall')" class="control-btn" style="font-size: 11px; padding: 2px 6px; margin-left: 5px;">🌟 Key Overall (18)</button>
                    <span style="margin-left: 15px; font-size: 11px; color: #666;">|</span>
                    <button onclick="exportPreset()" class="control-btn" style="font-size: 11px; padding: 2px 6px; margin-left: 8px; background-color: #28a745; color: white;">💾 Export Preset</button>
                    <button onclick="importPreset()" class="control-btn" style="font-size: 11px; padding: 2px 6px; margin-left: 5px; background-color: #007bff; color: white;">📁 Import Preset</button>
                </div>
                <div>
                    <button onclick="toggleAllBuildingFilters(false)" class="control-btn" style="font-size: 11px; padding: 2px 6px; background-color: #d73027; color: white;">🗑 Clear All</button>
                </div>
            </div>
        </div>
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
                        display_name = self.get_building_display_name(building)
                        usage_count = building_counts.get(building, 0)
                        anchor_name = "building-{}".format(building)
                        # Use the existing building icon path method
                        icon_path = self.get_building_icon_path(building)
                        if not icon_path:
                            # Fallback if icon not found
                            building_key = building.replace('building_', '')
                            icon_path = "buildings/64px-Building_{}.png".format(building_key)
                        # Add checkbox for building filter
                        checkbox_id = "filter-{}".format(building)
                        html += '<li class="category-item">' \
                               '<input type="checkbox" id="{}" class="building-filter-checkbox" checked data-building="{}" onchange="toggleBuildingFilter(this)">' \
                               '<a href="#{}">' \
                               '<img src="{}" class="toc-building-icon" alt="{} icon">{} ({})' \
                               '</a></li>'.format(checkbox_id, building, anchor_name, icon_path, display_name, display_name, usage_count)
            
            html += '</ul></div>'
        
        html += '''
        </div>
    </div>'''
        
        # Generate hierarchical country/company filter section
        html += self._generate_country_filter_section(countries_by_continent)
        
        # Generate separate table for each building
        for building in buildings_to_analyze:
            display_name = self.get_building_display_name(building)
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
            
            # Get all buildings available to these companies (for columns) - ordered by logical wiki categories
            available_buildings_raw = self.get_all_buildings_for_companies(all_companies_with_building)
            
            # Use the same logical order as the summary section (wiki_building_order)
            available_buildings = []
            for wiki_building in wiki_building_order:
                if wiki_building in available_buildings_raw:
                    available_buildings.append(wiki_building)
            
            # Add any remaining buildings not in wiki order (safety net)
            for remaining_building in sorted(available_buildings_raw):
                if remaining_building not in available_buildings:
                    available_buildings.append(remaining_building)
            
            # Count usage within this specific company set (for tooltips)
            company_specific_counts = Counter()
            for company_name in all_companies_with_building:
                if company_name in self.companies:
                    data = self.companies[company_name]
                    for b in data['building_types']:
                        company_specific_counts[b] += 1
                    for b in data['extension_building_types']:
                        company_specific_counts[b] += 1
            
            # Get building icon for header
            building_icon_path = self.get_building_icon_path(building)
            building_icon_html = ''
            if building_icon_path:
                building_icon_html = '<img src="{}" style="width:32px;height:32px;vertical-align:middle;margin-right:10px;" alt="{} icon">'.format(building_icon_path, display_name)
            
            html += '''
    <div class="building-section" id="building-{}">
        <h2 id="{}">{}{} ({}) <a href="#custom-companies-section" class="back-to-top" title="Back to Selected Companies">↑ Back to Top</a></h2>
        
        <div class="table-container">
        <table class="building-table sortable">
            <thead>
                <tr>
                    <th class="select-column" title="Select Company">☐</th>
                    <th class="flag-column" title="Country">🏳️</th>
                    <th class="dynamic-coverage-column" title="Dynamic Coverage from Selected Companies">➕</th>
                    <th class="buildings-column" title="Base Coverage . Available Industry Charters">📊</th>
                    <th class="company-name">Company Name</th>'''.format(building, anchor_name, building_icon_html, display_name, len(all_companies_with_building))
            
            # Add columns for all buildings these companies can use (frequency ordered within this company set)
            for avail_building in available_buildings:
                icon_path = self.get_building_icon_path(avail_building)
                avail_display = avail_building.replace('building_', '').replace('_', ' ').title()
                usage_in_set = company_specific_counts.get(avail_building, 0)
                
                if icon_path:
                    header_style = 'style="background-image: url({})"'.format(icon_path)
                    header_class = 'building-header col-{}'.format(avail_building)
                else:
                    header_style = ''
                    header_class = 'building-header missing-icon col-{}'.format(avail_building)
                
                html += '''
                    <th class="{}" {} title="{} ({})" data-building="{}">
                    </th>'''.format(header_class, header_style, avail_display, usage_in_set, avail_building)
            
            
            html += '''
                </tr>
            </thead>
            <tbody>'''
            
            # Sort companies by building priority for this specific building
            def company_sort_key(company_name):
                data = self.companies[company_name]
                
                # Priority: companies with prestige > base > charter > blank
                # Check if company has prestige goods specifically for THIS building
                has_prestige = False
                if building in data['building_types']:  # Only base buildings can have prestige
                    prestige_result = self.company_has_prestige_for_building(company_name, building)
                    if prestige_result and isinstance(prestige_result, tuple) and prestige_result[0]:
                        has_prestige = True
                
                has_base = building in data['building_types']
                has_charter = building in data['extension_building_types']
                
                priority = 0
                if has_prestige:
                    priority = 3  # Prestige goods for this building
                elif has_base:
                    priority = 2  # Base building for this company
                elif has_charter:
                    priority = 1  # Charter building for this company
                # else priority = 0 (company doesn't have this building at all)
                
                # Get total building counts for tiebreaker (coverage number)
                base_count, charter_count, _ = self.get_company_building_stats(company_name)
                
                # Sort by priority first, then by total coverage (base.charter as decimal)
                # Within same priority level, sort by coverage: higher coverage first
                sort_key = (-priority, -base_count, -charter_count, company_name.replace('company_', '').lower())
                
                return sort_key
            
            sorted_company_names = sorted(all_companies_with_building, key=company_sort_key)
            
            # Generate rows for this building's table
            for company_name in sorted_company_names:
                data = self.companies[company_name]
                display_name = data.get('display_name', self.get_company_display_name(company_name))
                
                # Get prosperity bonuses for inline display  
                prosperity_bonuses_text = self.format_prosperity_bonuses(data.get('prosperity_bonuses', []))
                
                # Abbreviate long company names for display
                abbreviated_name = self.abbreviate_company_name(display_name, 35)
                
                # Get company building statistics and prestige goods
                base_count, charter_count, prestige_goods = self.get_company_building_stats(company_name)
                building_count_display = self.format_building_count(base_count, charter_count)
                prestige_icons = self.get_company_prestige_icons(company_name)
                
                # Add special requirement icons (after prestige icons)
                special_requirement_icons = ''
                special_reqs = data.get('special_requirements', [])
                if 'journal_entry' in special_reqs:
                    special_requirement_icons += '📚 '
                if 'primary_culture' in special_reqs:
                    special_requirement_icons += '🛑 '
                if data.get('starts_enacted', False):
                    special_requirement_icons += '⚠️ '
                
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
                
                # Get company country for filtering
                company_country = data.get('country', '')
                
                html += '''
            <tr data-country="{}" data-company="{}">
                <td class="select-column">
                    <input type="checkbox" class="company-checkbox" data-company="{}" onchange="toggleCompanySelection('{}')">
                </td>
                <td class="flag-column">{}</td>
                <td class="dynamic-coverage-column" data-company="{}">-</td>
                <td class="buildings-column">{}</td>
                <td class="company-name"
                    onmouseover="showCompanyTooltip(event, '{}')" 
                    onmouseout="hideCompanyTooltip()" 
                    data-company="{}">
                    {}{}{}{}
                </td>'''.format(company_country, company_name, company_name, company_name, flag_cell_html, company_name, building_count_display, company_name, company_name, company_icon_html, prestige_icons, special_requirement_icons, abbreviated_name)
                
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
                        cell_class = "prestige-building col-{}".format(avail_building)
                        html += '<td class="{}" data-building="{}">{}</td>'.format(cell_class, avail_building, cell_content)
                    elif has_base and has_extension:
                        # Company has both base and charter - show charter selection UI
                        cell_content = "&#x25CB;"  # Will be updated by JavaScript based on selection
                        cell_class = "base-building charter-selectable col-{}".format(avail_building)
                        onclick_attr = 'onclick="selectCharter(\'{}\', \'{}\')" style="cursor: pointer;"'.format(company_name, avail_building)
                        title_attr = 'title="Industry Charter: Click to select/deselect"'
                        html += '<td class="{}" {} {} data-building="{}">{}</td>'.format(cell_class, onclick_attr, title_attr, avail_building, cell_content)
                    elif has_base:
                        cell_content = "&#x25CF;"
                        cell_class = "base-building col-{}".format(avail_building)
                        html += '<td class="{}" data-building="{}">{}</td>'.format(cell_class, avail_building, cell_content)
                    elif has_extension:
                        # Extension only - show charter selection UI
                        cell_content = "&#x25CB;"  # Will be updated by JavaScript based on selection
                        cell_class = "extension-building charter-selectable"
                        onclick_attr = 'onclick="selectCharter(\'{}\', \'{}\')" style="cursor: pointer;"'.format(company_name, avail_building)
                        title_attr = 'title="Industry Charter: Click to select/deselect"'
                        html += '<td class="{} col-{}" {} {} data-building="{}">{}</td>'.format(cell_class, avail_building, onclick_attr, title_attr, avail_building, cell_content)
                    else:
                        # No building relationship
                        html += '<td class="col-{}" data-building="{}"></td>'.format(avail_building, avail_building)
                
                html += '</tr>'
            
            html += '''
            </tbody>
        </table>
        </div>
    </div>'''
        
        html += '''
    
    <script>
__YALPS_BUNDLE_PLACEHOLDER__
    </script>
    
    <script>
        // YALPS bundled library is included above
        // We will ONLY use YALPS, no other solvers
        
        // YALPS is loaded from the bundled library above - NO OTHER IMPLEMENTATIONS
        
        // All fake solvers have been removed - ONLY USE window.YALPS.solve()
        // Company data for tooltips
        const companyData = {'''
        
        # Add company data for tooltips
        company_entries = []
        for company_name, data in self.companies.items():
            display_name = data.get('display_name', self.get_company_display_name(company_name))
            requirements_json = json.dumps(data['formation_requirements'])
            bonuses_json = json.dumps(data['prosperity_bonuses'])
            
            # Get formatted prosperity bonuses for inline display
            prosperity_bonuses_text = self.format_prosperity_bonuses(data.get('prosperity_bonuses', []))
            prosperity_bonuses_text_json = json.dumps(prosperity_bonuses_text)
            
            country_info = ""  # Remove confidence display - country is definitive from game files
            
            # Add building information for detailed tooltip
            prestige_goods_json = json.dumps(data.get('possible_prestige_goods', []))
            building_types_json = json.dumps(data.get('building_types', []))
            extension_building_types_json = json.dumps(data.get('extension_building_types', []))
            
            # Add special requirements and starts enacted for JavaScript access
            special_requirements_json = json.dumps(data.get('special_requirements', []))
            starts_enacted_json = json.dumps(data.get('starts_enacted', False))
            
            entry = '''            {}: {{
                "name": {},
                "country": {},
                "country_confidence": {},
                "country_info": {},
                "requirements": {},
                "bonuses": {},
                "prosperity_bonuses_text": {},
                "prestige_goods": {},
                "building_types": {},
                "extension_building_types": {},
                "base_buildings": {},
                "industry_charters": {},
                "special_requirements": {},
                "starts_enacted": {}
            }}'''.format(json.dumps(company_name), json.dumps(display_name), json.dumps(data["country"] or ""), json.dumps(data["country_confidence"]), json.dumps(country_info), requirements_json, bonuses_json, prosperity_bonuses_text_json, prestige_goods_json, building_types_json, extension_building_types_json, building_types_json, extension_building_types_json, special_requirements_json, starts_enacted_json)
            company_entries.append(entry)
        
        html += ',\n'.join(company_entries)
        html += '''
        };
        
        // Global country mappings for flags and names
        const countryFlags = ''' + self._get_country_flags_js() + ''';
        const countryNames = ''' + self._get_country_names_js() + ''';
        
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
                
                // Generate special requirement icons for header
                let specialIcons = '';
                if (data.special_requirements && data.special_requirements.length > 0) {
                    data.special_requirements.forEach(req => {
                        if (req === 'journal_entry') specialIcons += '📚 ';
                        else if (req === 'primary_culture') specialIcons += '🛑 ';
                        else if (req === 'law' || req === 'ideology' || req === 'diplomatic') specialIcons += '🔒 ';
                    });
                }
                
                // Add pre-enacted icon
                if (data.starts_enacted) {
                    specialIcons += '⚠️ ';
                }
                
                html = `
                    <h3>
                        ${iconElement}
                        <div class="company-details">
                            ${specialIcons}${data.name}
                            ${countryDisplay}
                        </div>
                    </h3>
                `;
                
                if (data.requirements && data.requirements.length > 0) {
                    html += '<div class="requirements"><h4>Formation Requirements</h4><ul>';
                    data.requirements.forEach(req => {
                        let icon = '';
                        // Add icons for specific requirement types
                        if (req.includes('Primary culture:')) {
                            icon = '🛑 ';
                        } else if (req.includes('Technology:')) {
                            icon = '💡 ';
                        } else if (req.includes('journal entry') || req.includes('Journal Entry')) {
                            icon = '📚 ';
                        } else if (req.includes('Starts Enacted') || req.includes('game start')) {
                            icon = '⚠️ ';
                        }
                        html += `<li>${icon}${req}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                if (data.bonuses && data.bonuses.length > 0) {
                    html += '<div class="bonuses"><h4>Prosperity Bonuses</h4><ul>';
                    data.bonuses.forEach(bonus => {
                        html += `<li>${bonus}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // Add special requirements section
                if (data.special_requirements && data.special_requirements.length > 0) {
                    const reqIcons = {
                        'journal_entry': '📚',
                        'primary_culture': '🛑',
                        'technology': '💡',
                        'law': '🔒',
                        'ideology': '🔒',
                        'diplomatic': '🔒'
                    };
                    
                    const reqNames = {
                        'journal_entry': 'Journal Entry Required',
                        'primary_culture': 'Primary Culture Required',
                        'technology': 'Technology Required',
                        'law': 'Law Required',
                        'ideology': 'Ideology Required',
                        'diplomatic': 'Diplomatic Status Required',
                        'regional': 'Regional Interest Required'
                    };
                    
                    html += '<div class="special-requirements"><h4>Special Requirements</h4><ul>';
                    data.special_requirements.forEach(req => {
                        const icon = reqIcons[req] || '';
                        const name = reqNames[req] || req;
                        html += `<li>${icon} ${name}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // Add pre-enacted status
                if (data.starts_enacted) {
                    html += '<div class="pre-enacted"><h4>Status</h4><ul>';
                    html += '<li>⚠️ Established at Game Start</li>';
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
                        const buildingName = getBuildingDisplayName(building);
                        
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
                        const charterName = getBuildingDisplayName(charter);
                        
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
        
        // Custom Company Collection functionality
        const STORAGE_KEY = 'v3-custom-companies';
        const CHARTER_STORAGE_KEY = 'v3-selected-charters';
        
        function getCustomCompanies() {
            try {
                return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            } catch {
                return [];
            }
        }
        
        function saveCustomCompanies(companies) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(companies));
        }
        
        function getSelectedCharters() {
            try {
                return JSON.parse(localStorage.getItem(CHARTER_STORAGE_KEY) || '{}');
            } catch {
                return {};
            }
        }
        
        function saveSelectedCharters(charters) {
            localStorage.setItem(CHARTER_STORAGE_KEY, JSON.stringify(charters));
        }
        
        function selectCharter(companyName, building) {
            const customCompanies = getCustomCompanies();
            console.log('selectCharter called:', companyName, building);
            console.log('customCompanies at charter selection:', customCompanies);
            
            // Only allow charter selection for companies that are already selected
            if (!customCompanies.includes(companyName)) {
                console.log('Company not selected, returning');
                return; // Do nothing if company is not selected
            }
            
            const selectedCharters = getSelectedCharters();
            console.log('selectedCharters before change:', selectedCharters);
            // Toggle selection: if clicking same charter, deselect it
            if (selectedCharters[companyName] === building) {
                delete selectedCharters[companyName];
            } else {
                selectedCharters[companyName] = building;
            }
            console.log('selectedCharters after change:', selectedCharters);
            saveSelectedCharters(selectedCharters);
            console.log('Charter saved, calling updates...');
            updateCustomTable();
            updateDynamicCoverage();
            updateMainBuildingHeaders();
            updateBuildingTableCharters();
        }
        
        function updateBuildingTableCharters() {
            const selectedCharters = getSelectedCharters();
            const customCompanies = getCustomCompanies();
            
            // Update all charter-selectable cells in building tables
            document.querySelectorAll('.charter-selectable').forEach(cell => {
                const onclick = cell.getAttribute('onclick');
                if (onclick) {
                    // Extract company name and building from onclick attribute
                    const match = onclick.match(/selectCharter\('([^']+)', '([^']+)'\)/);
                    if (match) {
                        const companyName = match[1];
                        const building = match[2];
                        const isCompanySelected = customCompanies.includes(companyName);
                        const selectedCharter = selectedCharters[companyName];
                        
                        // Update cell appearance based on company selection and charter state
                        if (!isCompanySelected) {
                            // Company not selected - show grayed out, not clickable
                            cell.innerHTML = "&#x25CB;";
                            cell.className = cell.className.replace(/\b(selected-charter|dimmed-charter|clickable-charter)\b/g, '').trim() + ' unselected-company';
                            cell.title = "Industry Charter: Company must be selected first";
                            cell.style.opacity = "0.2";
                            cell.style.cursor = "default";
                        } else if (selectedCharter === building) {
                            // This charter is selected - show filled circle
                            cell.innerHTML = "&#x25CF;";
                            cell.className = cell.className.replace(/\b(selected-charter|dimmed-charter|clickable-charter|unselected-company)\b/g, '').trim() + ' selected-charter';
                            cell.title = "Industry Charter: Click to deselect";
                            cell.style.opacity = "1";
                            cell.style.cursor = "pointer";
                        } else if (selectedCharter) {
                            // Another charter is selected - show dimmed hollow circle
                            cell.innerHTML = "&#x25CB;";
                            cell.className = cell.className.replace(/\b(selected-charter|dimmed-charter|clickable-charter|unselected-company)\b/g, '').trim() + ' dimmed-charter';
                            cell.title = "Industry Charter: Another charter selected";
                            cell.style.opacity = "0.3";
                            cell.style.cursor = "pointer";
                        } else {
                            // No charter selected - show clickable hollow circle
                            cell.innerHTML = "&#x25CB;";
                            cell.className = cell.className.replace(/\b(selected-charter|dimmed-charter|clickable-charter|unselected-company)\b/g, '').trim() + ' clickable-charter';
                            cell.title = "Industry Charter: Click to select";
                            cell.style.opacity = "1";
                            cell.style.cursor = "pointer";
                        }
                    }
                }
            });
        }
        
        function updateMainBuildingHeaders() {
            const selectedCompanies = getCustomCompanies();
            const selectedCharters = getSelectedCharters();
            const companyData = ''' + self._get_company_data_js() + ''';
            
            // Calculate covered buildings
            const coveredBuildings = new Set();
            selectedCompanies.forEach(companyName => {
                const company = companyData[companyName];
                if (company) {
                    // Add base buildings to covered set
                    if (company.building_types) {
                        company.building_types.forEach(building => {
                            coveredBuildings.add(building);
                        });
                    }
                    
                    // Add selected charter building to covered set
                    const selectedCharter = selectedCharters[companyName];
                    if (selectedCharter) {
                        coveredBuildings.add(selectedCharter);
                    }
                }
            });
            
            // Update building section headers with filtered company counts
            updateBuildingSectionCounts();
            
            // Update all building headers in main tables
            document.querySelectorAll('th[data-building].building-header').forEach(header => {
                const building = header.getAttribute('data-building');
                const isCovered = coveredBuildings.has(building);
                
                if (isCovered) {
                    header.classList.add('covered');
                    // Update tooltip to show covered status
                    const currentTitle = header.getAttribute('title') || '';
                    if (!currentTitle.includes('(Covered)')) {
                        header.setAttribute('title', currentTitle + ' (Covered)');
                    }
                } else {
                    header.classList.remove('covered');
                    // Remove covered status from tooltip
                    const currentTitle = header.getAttribute('title') || '';
                    header.setAttribute('title', currentTitle.replace(' (Covered)', ''));
                }
            });
        }
        
        // Building display name overrides
        function getBuildingDisplayName(building) {
            const displayNameOverrides = {
                'building_chemical_plants': 'Fertilizer Plants'
            };
            
            if (displayNameOverrides[building]) {
                return displayNameOverrides[building];
            } else {
                return building.replace('building_', '').replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
            }
        }
        
        // Building filter functions
        function toggleBuildingFilter(checkbox) {
            const building = checkbox.dataset.building;
            const isChecked = checkbox.checked;
            
            console.log(`Toggle ${building}: checked=${isChecked}`);
            
            // Add/remove CSS class to control column visibility
            if (isChecked) {
                document.body.classList.remove(`hide-building-${building}`);
                console.log(`Removed class: hide-building-${building}`);
            } else {
                document.body.classList.add(`hide-building-${building}`);
                console.log(`Added class: hide-building-${building}`);
                console.log(`Body classes:`, document.body.className);
                console.log(`Elements with .col-${building}:`, document.querySelectorAll(`.col-${building}`).length);
            }
            
            // Hide/show building sections
            const buildingSection = document.getElementById(`building-${building}`);
            if (buildingSection) {
                buildingSection.style.display = isChecked ? '' : 'none';
            }
            
            // Update dynamic coverage calculations
            updateDynamicCoverage();
            updateCustomTable();
            updateBuildingCount();
        }
        
        function toggleAllBuildingFilters(selectAll) {
            const checkboxes = document.querySelectorAll('.building-filter-checkbox');
            checkboxes.forEach(checkbox => {
                if (checkbox.checked !== selectAll) {
                    checkbox.checked = selectAll;
                    
                    // Update visibility for this building without calling full update functions
                    const building = checkbox.dataset.building;
                    
                    // Add/remove CSS class to control column visibility
                    if (selectAll) {
                        document.body.classList.remove(`hide-building-${building}`);
                    } else {
                        document.body.classList.add(`hide-building-${building}`);
                    }
                    
                    // Hide/show building sections
                    const buildingSection = document.getElementById(`building-${building}`);
                    if (buildingSection) {
                        buildingSection.style.display = selectAll ? '' : 'none';
                    }
                }
            });
            
            // Update calculations once after all checkboxes are processed
            updateDynamicCoverage();
            updateCustomTable();
            updateBuildingCount();
        }
        
        function updateBuildingCount() {
            const checkboxes = document.querySelectorAll('.building-filter-checkbox:checked');
            const count = checkboxes.length;
            const countElement = document.getElementById('selected-buildings-count');
            if (countElement) {
                countElement.textContent = count;
            }
        }
        
        function getEnabledBuildings() {
            const enabledBuildings = [];
            const checkboxes = document.querySelectorAll('.building-filter-checkbox:checked');
            checkboxes.forEach(checkbox => {
                enabledBuildings.push(checkbox.dataset.building);
            });
            return enabledBuildings;
        }
        
        // Country filter functions
        function toggleCountryFilter(checkbox) {
            const country = checkbox.dataset.country;
            const isChecked = checkbox.checked;
            
            console.log(`Toggle country ${country}: checked=${isChecked}`);
            
            // Add/remove CSS class to control company visibility
            if (isChecked) {
                document.body.classList.remove(`hide-country-${country}`);
            } else {
                document.body.classList.add(`hide-country-${country}`);
            }
            
            // Update continent checkbox based on country selections
            updateContinentCheckboxes();
            
            // Update count and refresh tables
            updateCountryCount();
            updateMainBuildingHeaders();
            updateCustomTable();
        }
        
        function updateContinentCheckboxes() {
            const continents = ['American', 'Asian_Oceanian', 'European', 'Middle_Eastern'];
            continents.forEach(continent => {
                const continentCheckbox = document.getElementById(`continent-${continent}`);
                const continentCountSpan = document.getElementById(`continent-count-${continent}`);
                
                if (continentCheckbox) {
                    // Use correct selector for Countries & Companies section
                    const countryCheckboxes = document.querySelectorAll(`.country-checkbox`);
                    const checkedCountries = document.querySelectorAll(`.country-checkbox:checked`);
                    
                    // Update checkbox state
                    if (checkedCountries.length === 0) {
                        continentCheckbox.checked = false;
                        continentCheckbox.indeterminate = false;
                    } else if (checkedCountries.length === countryCheckboxes.length) {
                        continentCheckbox.checked = true;
                        continentCheckbox.indeterminate = false;
                    } else {
                        continentCheckbox.checked = false;
                        continentCheckbox.indeterminate = true;
                    }
                    
                    // Update count display - count companies from checked countries, not countries
                    if (continentCountSpan) {
                        let companyCount = 0;
                        checkedCountries.forEach(countryCheckbox => {
                            const countryCode = countryCheckbox.dataset.country;
                            // Count companies from this country
                            for (const [companyName, company] of Object.entries(companyData)) {
                                if (company.country === countryCode && !companyName.startsWith('company_basic_')) {
                                    companyCount++;
                                }
                            }
                        });
                        continentCountSpan.textContent = companyCount;
                    }
                }
            });
        }
        
        function toggleAllCountryFilters(selectAll) {
            const checkboxes = document.querySelectorAll('.country-filter-checkbox');
            checkboxes.forEach(checkbox => {
                if (checkbox.checked !== selectAll) {
                    checkbox.checked = selectAll;
                    
                    const country = checkbox.dataset.country;
                    
                    if (selectAll) {
                        document.body.classList.remove(`hide-country-${country}`);
                    } else {
                        document.body.classList.add(`hide-country-${country}`);
                    }
                }
            });
            
            // Update continent checkboxes after global change
            updateContinentCheckboxes();
            updateCountryCount();
            updateMainBuildingHeaders();
            updateCustomTable();
        }
        
        function updateCountryCount() {
            const checkboxes = document.querySelectorAll('.country-filter-checkbox:checked');
            const count = checkboxes.length;
            const countElement = document.getElementById('selected-countries-count');
            if (countElement) {
                countElement.textContent = count;
            }
        }
        
        // Hierarchical Company Filter Functions
        function toggleCountryExpansion(countryCode) {
            const companiesList = document.getElementById(`companies-${countryCode}`);
            const expandIcon = document.getElementById(`expand-${countryCode}`);
            
            if (companiesList.style.display === 'none') {
                companiesList.style.display = 'block';
                expandIcon.textContent = '▼';
            } else {
                companiesList.style.display = 'none';
                expandIcon.textContent = '▶';
            }
        }
        
        function toggleAllCompaniesInCountry(countryCheckbox) {
            const countryCode = countryCheckbox.dataset.country;
            const isChecked = countryCheckbox.checked;
            
            // Toggle all company checkboxes in this country
            const companyCheckboxes = document.querySelectorAll(`input[data-country="${countryCode}"].company-checkbox`);
            companyCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
                updateCompanyVisibility(checkbox);
            });
            
            updateCountryStatus(countryCode);
            updateContinentStatus();
        }
        
        function updateCompanyFilter(companyCheckbox) {
            updateCompanyVisibility(companyCheckbox);
            
            const countryCode = companyCheckbox.dataset.country;
            if (countryCode === 'basic') {
                updateBasicCompaniesStatus();
            } else if (countryCode !== 'mandate') {
                updateCountryStatus(countryCode);
                updateCountryCheckbox(countryCode);
                updateContinentStatus();
            }
        }
        
        function updateBasicCompaniesStatus() {
            const basicCheckboxes = document.querySelectorAll('.company-checkbox[data-country="basic"]');
            const checkedBasic = document.querySelectorAll('.company-checkbox[data-country="basic"]:checked');
            const masterCheckbox = document.getElementById('all-basic-companies');
            
            if (masterCheckbox) {
                if (checkedBasic.length === 0) {
                    masterCheckbox.checked = false;
                    masterCheckbox.indeterminate = false;
                } else if (checkedBasic.length === basicCheckboxes.length) {
                    masterCheckbox.checked = true;
                    masterCheckbox.indeterminate = false;
                } else {
                    masterCheckbox.checked = false;
                    masterCheckbox.indeterminate = true;
                }
            }
        }
        
        function updateContinentStatus() {
            const continents = ['American', 'Asian_Oceanian', 'European', 'Middle_Eastern'];
            
            continents.forEach(continentCode => {
                const continentCheckbox = document.getElementById(`continent-${continentCode}`);
                if (!continentCheckbox) return;
                
                // Find all countries in this continent
                const continentDiv = continentCheckbox.closest('div[style*="flex: 1"]');
                const countryCheckboxes = continentDiv.querySelectorAll('.country-checkbox');
                const checkedCountries = continentDiv.querySelectorAll('.country-checkbox:checked');
                
                if (checkedCountries.length === 0) {
                    continentCheckbox.checked = false;
                    continentCheckbox.indeterminate = false;
                } else if (checkedCountries.length === countryCheckboxes.length) {
                    continentCheckbox.checked = true;
                    continentCheckbox.indeterminate = false;
                } else {
                    continentCheckbox.checked = false;
                    continentCheckbox.indeterminate = true;
                }
            });
        }
        
        function updateCompanyVisibility(companyCheckbox) {
            const companyKey = companyCheckbox.dataset.company;
            const isEnabled = companyCheckbox.checked;
            
            // Add/remove CSS class to hide company rows
            if (isEnabled) {
                document.body.classList.remove(`hide-company-${companyKey}`);
            } else {
                document.body.classList.add(`hide-company-${companyKey}`);
            }
        }
        
        function updateCountryStatus(countryCode) {
            const companyCheckboxes = document.querySelectorAll(`input[data-country="${countryCode}"].company-checkbox`);
            const enabledCompanies = document.querySelectorAll(`input[data-country="${countryCode}"].company-checkbox:checked`);
            
            const statusElement = document.getElementById(`country-status-${countryCode}`);
            if (statusElement) {
                statusElement.textContent = `${enabledCompanies.length}/${companyCheckboxes.length} companies`;
            }
        }
        
        function updateCountryCheckbox(countryCode) {
            const countryCheckbox = document.getElementById(`country-${countryCode}`);
            const companyCheckboxes = document.querySelectorAll(`input[data-country="${countryCode}"].company-checkbox`);
            const enabledCompanies = document.querySelectorAll(`input[data-country="${countryCode}"].company-checkbox:checked`);
            
            if (countryCheckbox) {
                if (enabledCompanies.length === 0) {
                    countryCheckbox.checked = false;
                    countryCheckbox.indeterminate = false;
                } else if (enabledCompanies.length === companyCheckboxes.length) {
                    countryCheckbox.checked = true;
                    countryCheckbox.indeterminate = false;
                } else {
                    countryCheckbox.checked = false;
                    countryCheckbox.indeterminate = true;
                }
            }
        }
        
        function toggleAllCompanyFilters(enable) {
            const companyCheckboxes = document.querySelectorAll('.company-checkbox');
            companyCheckboxes.forEach(checkbox => {
                checkbox.checked = enable;
                updateCompanyVisibility(checkbox);
            });
            
            // Update all country statuses and checkboxes
            const countries = new Set();
            companyCheckboxes.forEach(checkbox => countries.add(checkbox.dataset.country));
            countries.forEach(countryCode => {
                updateCountryStatus(countryCode);
                updateCountryCheckbox(countryCode);
            });
            
            // Update Selected Companies count and display
            updateCustomTable();
            updateCheckboxes();
            updateControlButtons();
            updateDynamicCoverage();
            updateBuildingTableCharters();
            
            // Update all continent checkboxes
            const continentCheckboxes = document.querySelectorAll('.continent-checkbox');
            continentCheckboxes.forEach(checkbox => {
                checkbox.checked = enable;
            });
        }
        
        function toggleAllBasicCompanies(checkbox) {
            const isChecked = checkbox.checked;
            const basicCheckboxes = document.querySelectorAll('.company-checkbox[data-country="basic"]');
            basicCheckboxes.forEach(companyCheckbox => {
                companyCheckbox.checked = isChecked;
                updateCompanyVisibility(companyCheckbox);
            });
        }
        
        function toggleAllCompaniesInContinent(continentCheckbox) {
            const continentCode = continentCheckbox.dataset.continent;
            const isChecked = continentCheckbox.checked;
            
            // Find all countries in this continent by looking for country checkboxes within the continent's div
            const continentDiv = continentCheckbox.closest('div[style*="flex: 1"]');
            const countryCheckboxes = continentDiv.querySelectorAll('.country-checkbox');
            
            countryCheckboxes.forEach(countryCheckbox => {
                countryCheckbox.checked = isChecked;
                toggleAllCompaniesInCountry(countryCheckbox);
            });
        }
        
        function toggleCompanyCategory(category, enable) {
            let companyCheckboxes;
            
            if (category === 'basic_only') {
                // First disable all companies
                Array.from(document.querySelectorAll('.company-checkbox')).forEach(checkbox => {
                    checkbox.checked = false;
                    updateCompanyVisibility(checkbox);
                });
                // Then enable only basic companies (no mandate requirements) - but actually enable them
                companyCheckboxes = Array.from(document.querySelectorAll('.company-checkbox')).filter(checkbox => {
                    const companyId = checkbox.value;
                    return companyId.startsWith('company_basic_');
                });
                // Force enable to true for basic companies
                enable = true;
            } else if (category === 'pre_enacted') {
                // Find companies with ⚠️ indicator (pre-enacted)
                companyCheckboxes = Array.from(document.querySelectorAll('.company-checkbox')).filter(checkbox => {
                    const span = checkbox.nextElementSibling;
                    return span && span.textContent.includes('⚠️');
                });
            } else if (category === 'culture_restricted') {
                // Find companies with 🛑 indicator (primary culture required)
                companyCheckboxes = Array.from(document.querySelectorAll('.company-checkbox')).filter(checkbox => {
                    const span = checkbox.nextElementSibling;
                    return span && span.textContent.includes('🛑');
                });
            } else if (category === 'journal_required') {
                // Find companies with 📚 indicator (journal entry required)
                companyCheckboxes = Array.from(document.querySelectorAll('.company-checkbox')).filter(checkbox => {
                    const span = checkbox.nextElementSibling;
                    return span && span.textContent.includes('📚');
                });
            } else {
                companyCheckboxes = document.querySelectorAll(`.company-checkbox[data-category="${category}"]`);
            }
            
            companyCheckboxes.forEach(checkbox => {
                checkbox.checked = enable;
                updateCompanyVisibility(checkbox);
            });
            
            // Update all country statuses and checkboxes
            const countries = new Set();
            companyCheckboxes.forEach(checkbox => countries.add(checkbox.dataset.country));
            countries.forEach(countryCode => {
                updateCountryStatus(countryCode);
                updateCountryCheckbox(countryCode);
            });
            
            // Update Selected Companies count and display
            updateCustomTable();
            updateCheckboxes();
            updateControlButtons();
            updateDynamicCoverage();
            updateBuildingTableCharters();
        }
        
        function getEnabledCompanies() {
            const enabledCompanies = [];
            const checkboxes = document.querySelectorAll('.company-checkbox:checked');
            checkboxes.forEach(checkbox => {
                enabledCompanies.push(checkbox.dataset.company);
            });
            return enabledCompanies;
        }
        
        function getEnabledCountries() {
            const enabledCountries = [];
            const checkboxes = document.querySelectorAll('.country-filter-checkbox:checked');
            checkboxes.forEach(checkbox => {
                enabledCountries.push(checkbox.dataset.country);
            });
            return enabledCountries;
        }
        
        function toggleContinentFilter(continentCheckbox) {
            const continentKey = continentCheckbox.dataset.continent;
            const selectAll = continentCheckbox.checked;
            
            const checkboxes = document.querySelectorAll(`.country-filter-checkbox[data-continent="${continentKey}"]`);
            checkboxes.forEach(checkbox => {
                if (checkbox.checked !== selectAll) {
                    checkbox.checked = selectAll;
                    
                    const country = checkbox.dataset.country;
                    
                    if (selectAll) {
                        document.body.classList.remove(`hide-country-${country}`);
                    } else {
                        document.body.classList.add(`hide-country-${country}`);
                    }
                }
            });
            
            updateCountryCount();
            updateMainBuildingHeaders();
            updateCustomTable();
        }
        
        function updateBuildingSectionCounts() {
            // Update the company counts in building section headers based on country filters
            document.querySelectorAll('.building-section').forEach(section => {
                const buildingId = section.id;
                if (buildingId && buildingId.startsWith('building-')) {
                    const building = buildingId.replace('building-', '');
                    const header = section.querySelector('h2');
                    const table = section.querySelector('table');
                    
                    if (header && table) {
                        // Count visible (non-filtered) companies in this building's table
                        const visibleRows = table.querySelectorAll('tbody tr:not([style*="display: none"])');
                        const visibleCount = visibleRows.length;
                        
                        // Update the header text with the new count
                        const headerText = header.textContent;
                        const newHeaderText = headerText.replace(/\(\d+\)/, `(${visibleCount})`);
                        header.innerHTML = header.innerHTML.replace(/\(\d+\)/, `(${visibleCount})`);
                    }
                }
            });
        }
        
        // Building filter presets
        function applyBuildingPreset(presetName) {
            const presets = {
                'all_buildings': ''' + str(wiki_building_order).replace("'", '"') + ''',
                'key_economy': [
                    'building_coal_mine',
                    'building_iron_mine', 
                    'building_logging_camp',
                    'building_oil_rig',
                    'building_rubber_plantation',
                    'building_railway',
                    'building_power_plant',
                    'building_automotive_industry',
                    'building_explosives_factory',
                    'building_glassworks',
                    'building_motor_industry',
                    'building_steel_mills',
                    'building_tooling_workshops'
                ],
                'key_overall': [
                    'building_coal_mine',
                    'building_iron_mine', 
                    'building_logging_camp',
                    'building_oil_rig',
                    'building_rubber_plantation',
                    'building_railway',
                    'building_power_plant',
                    'building_automotive_industry',
                    'building_explosives_factory',
                    'building_glassworks',
                    'building_motor_industry',
                    'building_steel_mills',
                    'building_tooling_workshops',
                    'building_port',
                    'building_trade_center',
                    'building_textile_mills',
                    'building_furniture_manufacturies',
                    'building_food_industry'
                ]
            };
            
            const selectedBuildings = presets[presetName];
            if (!selectedBuildings) return;
            
            // First uncheck all buildings
            const allCheckboxes = document.querySelectorAll('.building-filter-checkbox');
            allCheckboxes.forEach(checkbox => {
                const building = checkbox.dataset.building;
                const shouldCheck = selectedBuildings.includes(building);
                
                if (checkbox.checked !== shouldCheck) {
                    checkbox.checked = shouldCheck;
                    
                    // Add/remove CSS class to control column visibility
                    if (shouldCheck) {
                        document.body.classList.remove(`hide-building-${building}`);
                    } else {
                        document.body.classList.add(`hide-building-${building}`);
                    }
                    
                    // Hide/show building sections
                    const buildingSection = document.getElementById(`building-${building}`);
                    if (buildingSection) {
                        buildingSection.style.display = shouldCheck ? '' : 'none';
                    }
                }
            });
            
            // Update calculations once after all checkboxes are processed
            updateDynamicCoverage();
            updateCustomTable();
            updateBuildingCount();
        }
        
        // Preset export/import functions
        function exportPreset() {
            const customCompanies = getCustomCompanies();
            const selectedCharters = getSelectedCharters();
            const enabledBuildings = getEnabledBuildings();
            
            const preset = {
                companies: customCompanies,
                charters: selectedCharters,
                buildings: enabledBuildings,
                exportDate: new Date().toISOString(),
                version: '1.0'
            };
            
            // Generate filename based on building count (for building presets)
            const buildingCount = enabledBuildings.length;
            
            // Add date-time suffix
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            
            const filename = `preset-${buildingCount}-${year}${month}${day}-${hours}${minutes}${seconds}.json`;
            
            const blob = new Blob([JSON.stringify(preset, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        function importPreset() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.style.display = 'none';
            
            input.onchange = function(event) {
                const file = event.target.files[0];
                if (!file) return;
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        const preset = JSON.parse(e.target.result);
                        
                        // Validate preset structure
                        if (!preset.companies || !Array.isArray(preset.companies)) {
                            throw new Error('Invalid preset format: missing companies array');
                        }
                        
                        // Apply the preset
                        // 1. Set companies
                        localStorage.setItem(STORAGE_KEY, JSON.stringify(preset.companies));
                        
                        // 2. Set charters if available
                        if (preset.charters && typeof preset.charters === 'object') {
                            localStorage.setItem(CHARTER_STORAGE_KEY, JSON.stringify(preset.charters));
                        }
                        
                        // 3. Set building filters if available
                        if (preset.buildings && Array.isArray(preset.buildings)) {
                            // First uncheck all buildings
                            const allCheckboxes = document.querySelectorAll('.building-filter-checkbox');
                            allCheckboxes.forEach(checkbox => {
                                checkbox.checked = false;
                                const building = checkbox.dataset.building;
                                // Add CSS class to hide columns for this building
                                document.body.classList.add(`hide-building-${building}`);
                                const buildingSection = document.getElementById(`building-${building}`);
                                if (buildingSection) {
                                    buildingSection.style.display = 'none';
                                }
                            });
                            
                            // Then check only the buildings from the preset
                            preset.buildings.forEach(building => {
                                const checkbox = document.querySelector(`[data-building="${building}"]`);
                                if (checkbox && checkbox.classList.contains('building-filter-checkbox')) {
                                    checkbox.checked = true;
                                    // Remove CSS class to show columns for this building
                                    document.body.classList.remove(`hide-building-${building}`);
                                    const buildingSection = document.getElementById(`building-${building}`);
                                    if (buildingSection) {
                                        buildingSection.style.display = '';
                                    }
                                }
                            });
                        }
                        
                        // Update UI
                        updateCustomTable();
                        updateCheckboxes();
                        updateControlButtons();
                        updateDynamicCoverage();
                        updateMainBuildingHeaders();
                        updateBuildingTableCharters();
                        updateBuildingCount();
                        
                        const companyCount = preset.companies.length;
                        const buildingCount = preset.buildings ? preset.buildings.length : 'unknown';
                        alert(`Preset imported successfully!\\n\\nCompanies: ${companyCount}\\nBuildings: ${buildingCount}\\nExported: ${preset.exportDate ? new Date(preset.exportDate).toLocaleString() : 'unknown'}`);
                        
                    } catch (error) {
                        alert('Error importing preset: ' + error.message);
                    }
                };
                reader.readAsText(file);
                
                // Clean up
                document.body.removeChild(input);
            };
            
            document.body.appendChild(input);
            input.click();
        }
        
        function getBuildingIconPath(building) {
            // Building icon mappings for special cases (generated from Python)
            const buildingIconMappings = ''' + self._get_building_icon_mappings_js() + ''';
            
            // Check if we have a specific mapping
            const iconName = buildingIconMappings[building];
            if (iconName) {
                return `buildings/64px-Building_${iconName}.png`;
            }
            
            // Default building icon path logic
            const buildingName = building.replace('building_', '');
            return `buildings/64px-Building_${buildingName}.png`;
        }
        
        function toggleCompanySelection(companyName) {
            const customCompanies = getCustomCompanies();
            const index = customCompanies.indexOf(companyName);
            console.log('toggleCompanySelection called:', companyName);
            console.log('customCompanies before:', customCompanies);
            
            if (index > -1) {
                // Remove from collection
                customCompanies.splice(index, 1);
                console.log('Removing company');
                
                // Clear any charter selection for this company when it's deselected
                const selectedCharters = getSelectedCharters();
                if (selectedCharters[companyName]) {
                    delete selectedCharters[companyName];
                    saveSelectedCharters(selectedCharters);
                }
            } else {
                // Add to collection
                customCompanies.push(companyName);
                console.log('Adding company');
            }
            
            console.log('customCompanies after:', customCompanies);
            saveCustomCompanies(customCompanies);
            console.log('Company saved, calling updates...');
            updateCustomTable();
            updateCheckboxes();
            updateControlButtons();
            updateDynamicCoverage();
            updateMainBuildingHeaders();
            updateBuildingTableCharters();
        }
        
        function removeFromCustomCollection(companyName) {
            const customCompanies = getCustomCompanies();
            const index = customCompanies.indexOf(companyName);
            if (index > -1) {
                customCompanies.splice(index, 1);
                saveCustomCompanies(customCompanies);
                
                // Clear any charter selection for this company when it's deselected
                const selectedCharters = getSelectedCharters();
                if (selectedCharters[companyName]) {
                    delete selectedCharters[companyName];
                    saveSelectedCharters(selectedCharters);
                }
                
                updateCustomTable();
                updateAddButtons();
                updateDynamicCoverage();
                updateBuildingTableCharters();
            }
        }
        
        function getAllBuildingsForCompanies(companyNames) {
            const allBuildings = new Set();
            companyNames.forEach(companyName => {
                const company = companyData[companyName];
                if (company) {
                    company.base_buildings.forEach(building => allBuildings.add(building));
                    company.industry_charters.forEach(building => allBuildings.add(building));
                }
            });
            return allBuildings; // Return Set, not array
        }
        
        // Building coverage tracking for selected companies
        
        
        
        // Define building order by categories matching TOC structure (global scope for use in multiple functions)
        const buildingOrder = [
            // Row 1: Extraction + Infrastructure + Urban Facilities (15 buildings total)
            // Extraction (10 buildings)
            'building_coal_mine', 'building_fishing_wharf', 'building_gold_mine', 'building_iron_mine', 
            'building_lead_mine', 'building_logging_camp', 'building_oil_rig', 'building_rubber_plantation', 
            'building_sulfur_mine', 'building_whaling_station',
            // Infrastructure + Urban Facilities (5 buildings)
            'building_port', 'building_railway', 'building_trade_center', 'building_power_plant', 'building_arts_academy',
            
            // Row 2: Manufacturing Industries (18 buildings)  
            'building_arms_industry', 'building_artillery_foundries', 'building_automotive_industry', 
            'building_electrics_industry', 'building_explosives_factory', 'building_chemical_plants', 
            'building_food_industry', 'building_furniture_manufacturies', 'building_glassworks', 
            'building_military_shipyards', 'building_motor_industry', 'building_munition_plants', 
            'building_paper_mills', 'building_shipyards', 'building_steel_mills', 'building_synthetics_plants', 
            'building_textile_mills', 'building_tooling_workshops',
            
            // Row 3: Agriculture + Plantations + Ranches (16 buildings)
            'building_maize_farm', 'building_millet_farm', 'building_rice_farm', 'building_rye_farm', 'building_wheat_farm',
            'building_vineyard_plantation', 'building_banana_plantation', 'building_coffee_plantation', 'building_cotton_plantation', 
            'building_dye_plantation', 'building_opium_plantation', 'building_silk_plantation', 'building_sugar_plantation',
            'building_tea_plantation', 'building_tobacco_plantation', 'building_livestock_ranch'
        ];
        
        // Formation requirement to simple territorial name mapping
        function getSimpleTerritorialRequirement(requirement) {
            const territorialMappings = {
                // Direct state control
                "Control state STATE_BOHEMIA": "Bohemia",
                "Control state STATE_BUENOS_AIRES": "Buenos Aires", 
                "Control state STATE_SAXONY": "Saxony",
                "Control state STATE_NANJING": "Nanjing",
                "Control state STATE_ZHEJIANG": "Zhejiang",
                "Control state STATE_SUZHOU": "Suzhou",
                "Control state STATE_ILE_DE_FRANCE": "Île-de-France",
                "Control state STATE_ARKANSAS": "Arkansas",
                "Control state STATE_CONNECTICUT": "Connecticut",
                "Control state STATE_AUSTRIA": "Austria",
                "Control state STATE_KANSAI": "Kansai",
                "Control state STATE_HOME_COUNTIES": "Home Counties",
                "Control state STATE_SICILY": "Sicily",
                "Control state STATE_MICHIGAN": "Michigan",
                "Control state STATE_NEW_YORK": "New York",
                "Control state STATE_PENNSYLVANIA": "Pennsylvania",
                "Control state STATE_PANAMA": "Panama",
                "Control state STATE_MASSACHUSETTS": "Massachusetts",
                "Control state STATE_EAST_GALICIA": "East Galicia",
                "Control state STATE_SAO_PAULO": "São Paulo",
                "Control state STATE_RIO_DE_JANEIRO": "Rio de Janeiro",
                "Control state STATE_PERNAMBUCO": "Pernambuco",
                "Control state STATE_RIO_GRANDE_DO_SUL": "Rio Grande do Sul",
                "Control state STATE_POTOSI": "Potosí",
                "Control state STATE_SANTIAGO": "Santiago",
                "Control state STATE_MIRANDA": "Miranda",
                "Control state STATE_LA_PAMPA": "La Pampa",
                "Control state STATE_LIMA": "Lima",
                "Control state STATE_LOUISIANA": "Louisiana",
                "Control state STATE_NEW_JERSEY": "New Jersey",
                "Control state STATE_MARYLAND": "Maryland",
                "Control state STATE_DELAWARE": "Delaware",
                "Control state STATE_BALKH": "Balkh",
                "Control state STATE_FERGANA": "Fergana",
                "Control state STATE_URALSK": "Uralsk",
                "Control state STATE_ISFAHAN": "Isfahan",
                "Control state STATE_LEBANON": "Lebanon",
                "Control state STATE_SEOUL": "Seoul",
                "Control state STATE_SEMIRECHE": "Semireche",
                "Control state STATE_MOSCOW": "Moscow",
                "Control state STATE_LEINSTER": "Leinster",
                "Control state STATE_BAGHDAD": "Baghdad",
                "Control state STATE_MOSUL": "Mosul",
                "Control state STATE_BASRA": "Basra",
                "Control state STATE_KHUZESTAN": "Khuzestan",
                "Control state STATE_PIEDMONT": "Piedmont",
                "Control state STATE_LOMBARDY": "Lombardy",
                "Control state STATE_ISTRIA": "Istria",
                "Control state STATE_CONSTANTINE": "Constantine",
                "Control state STATE_BURGUNDY": "Burgundy",
                "Control state STATE_CHAMPAGNE": "Champagne",
                "Control state STATE_RHONE": "Rhône",
                "Control state STATE_PROVENCE": "Provence",
                "Control state STATE_FRENCH_LOW_COUNTRIES": "French Low Countries",
                "Control state STATE_CHUGOKU": "Chugoku",
                "Control state STATE_SINAI": "Sinai",
                
                // Regional control
                "Control region in Region La Plata (level 5+ buildings required)": "Region: La Plata",
                "Control region in Region Pacific Coast (level 5+ buildings required)": "Region: Pacific Coast", 
                "Control region in Region South China (level 5+ buildings required)": "Region: South China",
                "Control region in Region Bengal (level 5+ buildings required)": "Region: Bengal",
                "Control region in Region Bombay (level 5+ buildings required)": "Region: Bombay",
                "Control region in Region Brazil (level 5+ buildings required)": "Region: Brazil",
                "Control region in Region Central Asia (level 5+ buildings required)": "Region: Central Asia",
                "Control region in Region Central India (level 5+ buildings required)": "Region: Central India",
                "Control region in Region Congo (level 5+ buildings required)": "Region: Congo",
                "Control region in Region England (level 5+ buildings required)": "Region: England",
                "Control region in Region Ethiopia (level 5+ buildings required)": "Region: Ethiopia",
                "Control region in Region Indonesia (level 5+ buildings required)": "Region: Indonesia",
                "Control region in Region Madras (level 5+ buildings required)": "Region: Madras",
                "Control region in Region Manchuria (level 5+ buildings required)": "Region: Manchuria",
                "Control region in Region Mexico (level 5+ buildings required)": "Region: Mexico",
                "Control region in Region Niger (level 5+ buildings required)": "Region: Niger",
                "Control region in Region Nile Basin (level 5+ buildings required)": "Region: Nile Basin",
                "Control region in Region North China (level 5+ buildings required)": "Region: North China",
                "Control region in Region North Germany (level 5+ buildings required)": "Region: North Germany",
                "Control region in Region Persia (level 5+ buildings required)": "Region: Persia",
                "Control region in Region The Midwest (level 5+ buildings required)": "Region: The Midwest",
                "Control region in Region Balkans (level 5+ buildings required)": "Region: Balkans",
                
                // Journal requirements would go here when found
                // "Journal: Honorable Restoration": "Journal: Honorable Restoration",
                
                // Formation requirements
                "States with Pampas trait": "States with Pampas trait",
                "Primary culture: Yankee": "Primary culture: Yankee",
                "Primary culture: Dixie": "Primary culture: Dixie", 
                "Primary culture: Persian": "Primary culture: Persian",
                "Primary culture: British": "Primary culture: British",
                "Primary culture: French": "Primary culture: French",
                "Primary culture: Occitan": "Primary culture: Occitan",
                "Primary culture: Japanese": "Primary culture: Japanese",
                "Level 10+ Steel Mills required": "Level 10+ Steel Mills required",
                
                // Technology requirements are ignored (return null)
                "Technology: Railways": null,
                "Technology: Chemical Bleaching": null,
                "Technology: Central Planning": null,
                "Technology: Pumpjacks": null,
            };
            
            // Check direct mapping first
            if (territorialMappings.hasOwnProperty(requirement)) {
                return territorialMappings[requirement];
            }
            
            // Pattern-based fallbacks for common formats
            const stateMatch = requirement.match(/^Control state STATE_([A-Z_]+)$/);
            if (stateMatch) {
                let stateName = stateMatch[1];
                stateName = stateName.replace(/_/g, ' ').toLowerCase();
                stateName = stateName.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                console.warn(`Missing state mapping for: "${requirement}" -> suggested: "${stateName}"`);
                return stateName;
            }
            
            const regionMatch = requirement.match(/^Control region in Region ([^(]+) \(level 5\+ buildings required\)$/);
            if (regionMatch) {
                const regionName = regionMatch[1].trim();
                console.warn(`Missing region mapping for: "${requirement}" -> suggested: "Region: ${regionName}"`);
                return `Region: ${regionName}`;
            }
            
            // Skip technology requirements silently
            if (requirement.startsWith("Technology:")) {
                return null;
            }
            
            // Skip building level requirements silently  
            if (requirement.includes("Level 5+") && !requirement.includes("Control")) {
                return null;
            }
            
            // For unmapped requirements, log and return the original text as fallback
            console.warn(`Unmapped formation requirement: "${requirement}"`);
            return requirement;
        }
        
        function generateSummarySection(customCompanies) {
            if (customCompanies.length === 0) return '';
            
            const selectedCharters = getSelectedCharters();
            const baseBuildings = new Set();
            const charterBuildings = new Set();
            const allPrestigeGoods = new Set();
            const prestige_icon_paths = ''' + self._get_prestige_icon_mappings_js() + ''';
            
            // Building short forms mapping
            const buildingShortForms = {
                'building_coal_mine': 'Coal',
                'building_fishing_wharf': 'Fish',
                'building_gold_mine': 'Gold',
                'building_iron_mine': 'Iron',
                'building_lead_mine': 'Lead',
                'building_logging_camp': 'Wood',
                'building_oil_rig': 'Oil',
                'building_rubber_plantation': 'Rubber',
                'building_sulfur_mine': 'Sulfur',
                'building_whaling_station': 'Whaling',
                'building_arms_industry': 'Arms',
                'building_artillery_foundries': 'Artillery',
                'building_automotive_industry': 'Auto',
                'building_electrics_industry': 'Electric',
                'building_explosives_factory': 'Explosives',
                'building_chemical_plants': 'Fertilizer',
                'building_food_industry': 'Food',
                'building_furniture_manufacturies': 'Furniture',
                'building_glassworks': 'Glass',
                'building_military_shipyards': 'Mil. Shipyards',
                'building_motor_industry': 'Motors',
                'building_munition_plants': 'Munitions',
                'building_paper_mills': 'Paper',
                'building_shipyards': 'Shipyards',
                'building_steel_mills': 'Steel',
                'building_synthetics_plants': 'Synthetics',
                'building_textile_mills': 'Textiles',
                'building_tooling_workshops': 'Tools',
                'building_port': 'Port',
                'building_railway': 'Railway',
                'building_trade_center': 'Trade',
                'building_power_plant': 'Power',
                'building_arts_academy': 'Arts',
                'building_maize_farm': 'Maize',
                'building_millet_farm': 'Millet',
                'building_rice_farm': 'Rice',
                'building_rye_farm': 'Rye',
                'building_wheat_farm': 'Wheat',
                'building_vineyard_plantation': 'Wine',
                'building_banana_plantation': 'Banana',
                'building_coffee_plantation': 'Coffee',
                'building_cotton_plantation': 'Cotton',
                'building_dye_plantation': 'Dye',
                'building_opium_plantation': 'Opium',
                'building_silk_plantation': 'Silk',
                'building_sugar_plantation': 'Sugar',
                'building_tea_plantation': 'Tea',
                'building_tobacco_plantation': 'Tobacco',
                'building_livestock_ranch': 'Livestock'
            };
            
            // Function to get building short form
            const getBuildingShortForm = (building) => {
                return buildingShortForms[building] || building.replace('building_', '').replace(/_/g, ' ');
            };
            
            // Collect base buildings, charters, prestige goods and bonuses from selected companies
            // Only include buildings that are currently enabled by the building filter
            const enabledBuildings = getEnabledBuildings();
            const allProsperityBonuses = new Set();
            const prosperityBonusToCompanies = {}; // Track which companies provide which bonuses
            customCompanies.forEach(companyName => {
                const company = companyData[companyName];
                if (!company) return;
                
                // Add base buildings (only if enabled by filter)
                company.base_buildings.forEach(building => {
                    if (enabledBuildings.includes(building)) {
                        baseBuildings.add(building);
                    }
                });
                
                // Add selected charter if any (only if enabled by filter)
                const selectedCharter = selectedCharters[companyName];
                if (selectedCharter && company.industry_charters.includes(selectedCharter) && enabledBuildings.includes(selectedCharter)) {
                    charterBuildings.add(selectedCharter);
                }
                
                // Add prestige goods
                if (company.prestige_goods) {
                    company.prestige_goods.forEach(good => allPrestigeGoods.add(good));
                }
                
                // Add actual prosperity bonuses from companies and track source
                if (company.bonuses) {
                    company.bonuses.forEach(bonus => {
                        allProsperityBonuses.add(bonus);
                        if (!prosperityBonusToCompanies[bonus]) {
                            prosperityBonusToCompanies[bonus] = [];
                        }
                        prosperityBonusToCompanies[bonus].push(companyName);
                    });
                }
            });
            
            // Define category boundaries for three-row layout matching TOC structure
            const categoryRanges = {
                row1: { start: 0, end: 15 },   // Extraction (10) + Infrastructure (5) = 15 buildings
                row2: { start: 15, end: 33 },  // Manufacturing Industries = 18 buildings  
                row3: { start: 33, end: 49 }   // Agriculture + Plantations + Ranches = 16 buildings
            };
            
            // Track building sources and overlaps
            const buildingToCompanies = {};
            const overlaps = {};
            
            // Track base buildings by company
            customCompanies.forEach(companyName => {
                const company = companyData[companyName];
                if (!company) return;
                
                company.base_buildings.forEach(building => {
                    if (!buildingToCompanies[building]) buildingToCompanies[building] = [];
                    buildingToCompanies[building].push({company: companyName, type: 'base'});
                });
                
                // Track selected charters
                const selectedCharter = selectedCharters[companyName];
                if (selectedCharter && company.industry_charters.includes(selectedCharter)) {
                    if (!buildingToCompanies[selectedCharter]) buildingToCompanies[selectedCharter] = [];
                    buildingToCompanies[selectedCharter].push({company: companyName, type: 'charter'});
                }
            });
            
            // Find overlaps (buildings appearing in multiple companies)
            Object.keys(buildingToCompanies).forEach(building => {
                if (buildingToCompanies[building].length > 1) {
                    overlaps[building] = buildingToCompanies[building];
                }
            });
            
            // Generate building icons ONLY for enabled buildings with coverage status
            const coveredBuildings = new Set([...baseBuildings, ...charterBuildings]);
            let allBuildingIconsHTML = '';
            
            // Filter buildings to only show enabled ones
            const enabledBuildingsInOrder = buildingOrder.filter(building => enabledBuildings.includes(building));
            
            // Helper function to generate icons for enabled buildings only
            function generateIconsForEnabledBuildings(buildingsArray) {
                let iconsHTML = '';
                buildingsArray.forEach(building => {
                    const iconPath = getBuildingIconPath(building);
                    const displayName = getBuildingDisplayName(building);
                    const isCovered = coveredBuildings.has(building);
                    const isCharter = charterBuildings.has(building);
                    
                    let iconStyle = 'width: 32px; height: 32px; margin: 2px;';
                    let titleText = displayName;
                    
                    if (isCovered) {
                        if (isCharter) {
                            // Charter building - prominent yellow background only
                            iconStyle += ' background-color: #ffeaa7;';
                            titleText += ' (Charter)';
                        } else {
                            // Base building - normal appearance
                            titleText += ' (Base)';
                        }
                    } else {
                        // Not covered - grayed out
                        iconStyle += ' opacity: 0.3; filter: grayscale(100%);';
                        titleText += ' (Not covered)';
                    }
                    
                    iconsHTML += `<img src="${iconPath}" alt="${displayName}" title="${titleText}" style="${iconStyle}; cursor: pointer;" onclick="location.href='#building-${building}'" onerror="this.style.display='none'">`;
                });
                return iconsHTML;
            }
            
            // Generate single row with only enabled building icons
            allBuildingIconsHTML = '<div style="min-width: 700px;">' + generateIconsForEnabledBuildings(enabledBuildingsInOrder) + '</div>';
            
            // Generate prestige goods icons
            let prestigeIconsHTML = '';
            Array.from(allPrestigeGoods).sort().forEach(good => {
                const iconPath = prestige_icon_paths[good] || 'icons/40px-Goods_services.png';
                const displayName = good.replace('prestige_good_', '').replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                prestigeIconsHTML += `<img src="${iconPath}" alt="${displayName}" title="${displayName}" class="prestige-icon" style="width: 24px; height: 24px; margin: 2px;">`;
            });
            
            // Calculate totals - unique buildings only (don't double-count overlaps)
            const allUniqueBuildings = new Set([...baseBuildings, ...charterBuildings]);
            const totalPrestigeGoods = allPrestigeGoods.size;
            const totalBuildings = allUniqueBuildings.size;
            const totalOverlaps = Object.keys(overlaps).length;
            const actualBonuses = Array.from(allProsperityBonuses);
            
            let summaryHTML = '<div id="summary-section" style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 12px; margin: 16px 0; font-size: 13px; position: relative; min-width: 700px;">';
            
            // Collect country flags and state requirements for selected companies
            const countries = new Set();
            const stateRequirements = new Set();
            customCompanies.forEach(companyKey => {
                const company = companyData[companyKey];
                if (company && company.country) {
                    countries.add(company.country);
                }
                // Extract territorial requirements using mapping
                if (company && company.requirements) {
                    company.requirements.forEach(req => {
                        const territorialReq = getSimpleTerritorialRequirement(req);
                        if (territorialReq) {
                            stateRequirements.add(territorialReq);
                        }
                    });
                }
            });
            
            // Build title with flags and states
            let titleHTML = 'Selected Companies (' + customCompanies.length + ')';
            if (countries.size > 0) {
                titleHTML += ' ';
                Array.from(countries).forEach(country => {
                    const flag = countryFlags[country] || '';
                    const countryName = countryNames[country] || country;
                    if (flag) {
                        titleHTML += `<span title="${countryName}">${flag}</span> `;
                    }
                });
            }
            if (stateRequirements.size > 0) {
                titleHTML += '<span style="color: #666; font-weight: normal;">(' + Array.from(stateRequirements).sort().join(', ') + ')</span>';
            }
            summaryHTML += '<h4 style="margin: 0 0 8px 0; color: #495057; text-align: left;">' + titleHTML + '</h4>';
            
            // Keep the main title element simple (just company count)
            const mainTitleElement = document.getElementById('selected-companies-title');
            if (mainTitleElement) {
                mainTitleElement.textContent = `Selected Companies (${customCompanies.length})`;
            }
            
            // Compact buildings section - showing all buildings with coverage status
            // Use enabled buildings count instead of total buildings (49)
            const totalAvailableBuildings = enabledBuildings.length;
            summaryHTML += `<div style="margin-bottom: 8px;">`;
            summaryHTML += `<strong>Buildings (${totalBuildings}/${totalAvailableBuildings}):</strong> `;
            if (baseBuildings.size > 0) {
                summaryHTML += `${baseBuildings.size} base`;
                if (charterBuildings.size > 0) {
                    summaryHTML += `, ${charterBuildings.size} charters`;
                }
            } else if (charterBuildings.size > 0) {
                summaryHTML += `${charterBuildings.size} charters`;
            }
            summaryHTML += `, ${totalOverlaps} overlaps`;
            summaryHTML += `<br><div style="margin-top: 4px; min-width: 700px;">${allBuildingIconsHTML}</div>`;
            
            // Show overlap details if any exist
            if (totalOverlaps > 0) {
                summaryHTML += `<div style="margin-top: 6px; font-size: 12px; color: #666;">`;
                summaryHTML += `<strong>Overlaps:</strong> `;
                const overlapDetails = [];
                Object.keys(overlaps).forEach(building => {
                    const iconPath = getBuildingIconPath(building);
                    const buildingName = getBuildingDisplayName(building);
                    const count = overlaps[building].length;
                    const companies = overlaps[building].map(item => {
                        const companyIconPath = getCompanyIconPath(item.company);
                        const companyName = companyData[item.company]?.name || item.company;
                        return `<img src="${companyIconPath}" style="width: 16px; height: 16px; margin-right: 2px;" onerror="this.style.display='none'">${companyName}`;
                    }).join(', ');
                    overlapDetails.push(`${count}x <img src="${iconPath}" style="width: 16px; height: 16px; vertical-align: middle;" onerror="this.style.display='none'"> ${buildingName} (${companies})`);
                });
                summaryHTML += overlapDetails.join(', ');
                summaryHTML += `</div>`;
            }
            summaryHTML += `</div>`;
            
            // Prestige goods section (compact)
            if (totalPrestigeGoods > 0) {
                summaryHTML += `<div style="margin-bottom: 8px;">`;
                summaryHTML += `<strong>Prestige Goods (${totalPrestigeGoods}):</strong><br>`;
                summaryHTML += `<div style="margin-top: 4px;">${prestigeIconsHTML}</div>`;
                summaryHTML += `</div>`;
            }
            
            // Generate summary section with companies and optional prosperity bonuses
            if (customCompanies.length > 0) {
                summaryHTML += `<div style="margin-bottom: 8px;">`;
                summaryHTML += `<div style="display: flex; align-items: center; margin-bottom: 4px;">`;
                summaryHTML += `<strong>Summary:</strong>`;
                summaryHTML += `<label style="margin-left: 10px; font-size: 11px; cursor: pointer;">`;
                summaryHTML += `<input type="checkbox" id="show-prosperity-bonuses" onchange="regenerateSummaryContent()" style="margin-right: 4px;"> Show prosperity`;
                summaryHTML += `</label>`;
                summaryHTML += `</div>`;
                
                // Initial summary content will be generated by regenerateSummaryContent() after DOM is ready
                // This avoids the timing issue where checkbox state isn't available during initial generation
                
                summaryHTML += `<div id="summary-content" style="margin-top: 4px;"></div>`;
                summaryHTML += `</div>`;
                
                // Note: regenerateSummaryContent will be called from updateCustomTable() when needed
                // This ensures it runs after companies are loaded from any source (file, URL, localStorage)
            }
            
            
            // Add URL watermark for Selected Companies section
            summaryHTML += '<div style="position: absolute; bottom: 8px; right: 12px; font-size: 10px; color: #999; font-family: monospace; background: rgba(255,255,255,0.9); padding: 1px 4px; border-radius: 2px;">https://alcaras.github.io/v3co/</div>';
            
            summaryHTML += '</div>';
            return summaryHTML;
        }
        
        function updateCustomTable() {
            const customCompanies = getCustomCompanies();
            const customTableDiv = document.getElementById('custom-companies-table');
            
            // Note: Title is updated with flags in generateSummarySection, so we don't update it here to avoid overriding HTML
            
            // Update button states
            updateControlButtons();
            
            
            // Show/hide tutorial text based on whether companies are selected
            const tutorialText = document.getElementById('tutorial-text');
            if (customCompanies.length === 0) {
                if (tutorialText) tutorialText.style.display = 'block';
                customTableDiv.innerHTML = ''; // Clear any existing content
                return;
            } else {
                if (tutorialText) tutorialText.style.display = 'none';
            }
            // Get all buildings used by selected companies, ordered by logical categories
            const allBuildingsRaw = getAllBuildingsForCompanies(customCompanies);
            const allBuildings = [];
            
            // Get enabled buildings to filter the table
            const enabledBuildings = getEnabledBuildings();
            
            // Use same logical order as summary section and main tables
            buildingOrder.forEach(building => {
                if (allBuildingsRaw.has(building) && enabledBuildings.includes(building)) {
                    allBuildings.push(building);
                }
            });
            
            // Add any remaining buildings not in building order (safety net)
            Array.from(allBuildingsRaw).sort().forEach(building => {
                if (!allBuildings.includes(building) && enabledBuildings.includes(building)) {
                    allBuildings.push(building);
                }
            });
            
            let tableHTML = `
                <div class="table-container">
                    <table class="building-table sortable">
                        <thead>
                        <tr>
                            <th class="select-column" title="Remove Company">☑</th>
                            <th class="flag-column" title="Country">🏳️</th>
                            <th class="buildings-column" title="Base Coverage . Available Industry Charters">📊</th>
                            <th class="company-name">Company Name</th>`;
            
            allBuildings.forEach(building => {
                const displayName = getBuildingDisplayName(building);
                
                // Get building icon path (this will be generated from Python)
                const iconPath = getBuildingIconPath(building);
                if (iconPath) {
                    tableHTML += `<th class="building-header col-${building}" data-building="${building}" style="background-image: url(${iconPath})" title="${displayName}"></th>`;
                } else {
                    tableHTML += `<th class="building-header missing-icon col-${building}" data-building="${building}" title="${displayName}"></th>`;
                }
            });
            
            tableHTML += `</tr></thead><tbody>`;
            
            customCompanies.forEach(companyName => {
                const company = companyData[companyName];
                if (!company) return;
                
                const companyIconPath = getCompanyIconPath(companyName);
                const companyIconHTML = `<img src="${companyIconPath}" class="company-icon" alt="Company Icon" onerror="this.style.display='none'">`;
                
                // Calculate building count display like other tables (decimal format - fixed)
                // FIX: Use correct field names from global companyData
                const totalBuildings = (company.building_types || []).length + (company.extension_building_types || []).length;
                const baseCount = (company.building_types || []).length;
                const charters = (company.extension_building_types || []).length;
                const buildingCountDisplay = charters > 0 ? `${baseCount}.${charters}` : `${baseCount}`; // DECIMAL FORMAT FIX
                
                // Generate prestige icons using exact same logic as main tables
                let prestigeIcons = '';
                if (company.prestige_goods && company.prestige_goods.length > 0) {
                    // Prestige icon mappings pre-calculated from Python (same logic as main tables)
                    const prestigeIconPaths = ''' + self._get_prestige_icon_mappings_js() + ''';
                    
                    company.prestige_goods.forEach(good => {
                        const iconPath = prestigeIconPaths[good] || 'icons/40px-Goods_services.png';
                        const prestigeName = good.replace('prestige_good_', '').replace(/_/g, ' ');
                        prestigeIcons += `<img src="${iconPath}" width="16" height="16" alt="${prestigeName}" title="${prestigeName}" class="prestige-icon">`;
                    });
                }
                
                // Generate special requirement icons (after prestige icons)
                let specialRequirementIcons = '';
                if (company.special_requirements && Array.isArray(company.special_requirements)) {
                    if (company.special_requirements.includes('journal_entry')) {
                        specialRequirementIcons += '📚 ';
                    }
                    if (company.special_requirements.includes('primary_culture')) {
                        specialRequirementIcons += '🛑 ';
                    }
                }
                if (company.starts_enacted) {
                    specialRequirementIcons += '⚠️ ';
                }
                
                tableHTML += `<tr data-company="${companyName}" data-country="${company.country || ''}">
                    <td class="select-column">
                        <input type="checkbox" class="company-checkbox" data-company="${companyName}" onchange="toggleCompanySelection('${companyName}')" checked>
                    </td>`;
                
                // Flag column (draggable)
                tableHTML += `<td class="flag-column" draggable="true" ondragstart="dragStart(event)" ondragover="dragOver(event)" ondrop="dragDrop(event)" ondragend="dragEnd(event)">`;
                if (company.country) {
                    const countryFlags = ''' + self._get_country_flags_js() + ''';
                    const countryNames = ''' + self._get_country_names_js() + ''';
                    const flag = countryFlags[company.country] || '';
                    const countryName = countryNames[company.country] || company.country;
                    if (flag) {
                        tableHTML += `<span title="${countryName}">${flag}</span>`;
                    }
                }
                tableHTML += `</td>`;
                
                // Buildings column (draggable)
                tableHTML += `<td class="buildings-column" draggable="true" ondragstart="dragStart(event)" ondragover="dragOver(event)" ondrop="dragDrop(event)" ondragend="dragEnd(event)">${buildingCountDisplay}</td>`;
                
                // Company name column with tooltip (draggable)
                tableHTML += `<td class="company-name" draggable="true" ondragstart="dragStart(event)" ondragover="dragOver(event)" ondrop="dragDrop(event)" ondragend="dragEnd(event)"
                    onmouseover="showCompanyTooltip(event, '${companyName}')" 
                    onmouseout="hideCompanyTooltip()" 
                    data-company="${companyName}">
                    ${companyIconHTML}${prestigeIcons}${specialRequirementIcons}${company.name}
                </td>`;
                
                // Building columns with charter selection
                const selectedCharters = getSelectedCharters();
                const selectedCharter = selectedCharters[companyName];
                
                allBuildings.forEach(building => {
                    const hasBase = company.base_buildings.includes(building);
                    const hasExtension = company.industry_charters.includes(building);
                    let cellContent = "";
                    let cellClass = "";
                    let onClick = "";
                    let title = "";
                    let style = "";
                    
                    // Check if company has prestige goods for this building
                    let hasPrestige = false;
                    let prestigeGood = null;
                    if (hasBase && company.prestige_goods) {
                        // Use same prestige logic as main tables
                        const buildingToGoods = ''' + self._get_building_to_goods_js() + ''';
                        const prestigeToBase = ''' + self._get_prestige_to_base_goods_js() + ''';
                        
                        const buildingGood = buildingToGoods[building];
                        if (buildingGood) {
                            for (const prestige of company.prestige_goods) {
                                const baseGood = prestigeToBase[prestige];
                                if (baseGood === buildingGood) {
                                    hasPrestige = true;
                                    prestigeGood = prestige;
                                    break;
                                }
                            }
                        }
                    }
                    
                    if (hasPrestige && prestigeGood) {
                        // Show prestige icon instead of circle
                        const prestigeIconPaths = ''' + self._get_prestige_icon_mappings_js() + ''';
                        const iconPath = prestigeIconPaths[prestigeGood] || 'icons/40px-Goods_services.png';
                        const prestigeName = prestigeGood.replace('prestige_good_', '').replace(/_/g, ' ');
                        cellContent = `<img src="${iconPath}" width="16" height="16" alt="${prestigeName}" title="${prestigeName}">`;
                        cellClass = `prestige-building col-${building}`;
                        title = `Prestige Good: ${prestigeName}`;
                        style = '';
                        // No onClick for prestige buildings - they're always prestige
                    } else if (hasBase && hasExtension) {
                        if (selectedCharter === building) {
                            cellContent = "&#x25CF;"; // Filled circle for selected charter
                            cellClass = "base-building selected-charter";
                        } else if (selectedCharter) {
                            cellContent = "&#x25CB;"; // Hollow circle for dimmed unselected charter
                            cellClass = "base-building dimmed-charter";
                        } else {
                            cellContent = "&#x25CB;"; // Hollow circle for clickable charter
                            cellClass = "base-building clickable-charter";
                        }
                        onClick = `onclick="selectCharter('${companyName}', '${building}')"`;
                        title = `Industry Charter: Click to ${selectedCharter === building ? 'deselect' : 'select'}`;
                        style = 'cursor: pointer;';
                    } else if (hasBase) {
                        // Base building only - always present, not selectable
                        cellContent = "&#x25CF;";
                        cellClass = "base-building";
                        title = 'Base Building: Always available';
                        style = '';
                        // No onClick for base buildings - they're always available
                    } else if (hasExtension) {
                        if (selectedCharter === building) {
                            cellContent = "&#x25CF;"; // Filled circle for selected charter
                            cellClass = "extension-building selected-charter";
                        } else if (selectedCharter) {
                            cellContent = "&#x25CB;"; // Hollow circle for dimmed unselected
                            cellClass = "extension-building dimmed-charter";
                        } else {
                            cellContent = "&#x25CB;"; // Hollow circle for clickable
                            cellClass = "extension-building clickable-charter";
                        }
                        onClick = `onclick="selectCharter('${companyName}', '${building}')"`;
                        title = `Industry Charter: Click to ${selectedCharter === building ? 'deselect' : 'select'}`;
                        style = 'cursor: pointer;';
                    }
                    
                    tableHTML += `<td class="${cellClass} col-${building}" data-building="${building}" ${onClick} title="${title}" style="${style}">${cellContent}</td>`;
                });
                
                tableHTML += `</tr>`;
            });
            
            tableHTML += '</tbody></table></div>';
            
            // Add dynamic summary section
            tableHTML += generateSummarySection(customCompanies);
            
            // Schedule width adjustment for next frame to ensure table is rendered
            if (customCompanies.length > 0) {
                setTimeout(() => {
                    const summarySection = document.getElementById('summary-section');
                    const tableElement = document.querySelector('#custom-companies-table .building-table');
                    if (summarySection && tableElement) {
                        const tableWidth = tableElement.offsetWidth;
                        // Account for summary padding (12px left + 12px right = 24px) and border (2px)
                        const adjustedWidth = tableWidth - 26;
                        // Ensure minimum width is respected (700px min-width)
                        const finalWidth = Math.max(adjustedWidth, 700);
                        summarySection.style.width = finalWidth + 'px';
                    }
                }, 0);
            }
            
            // Only show instructions when no companies are selected
            if (customCompanies.length === 0) {
                tableHTML += '<p style="text-align: left; font-style: italic; color: #666; margin-top: 12px; font-size: 12px;">Click charters to select • Drag to reorder</p>';
            }
            customTableDiv.innerHTML = tableHTML;
            
            // Regenerate summary content whenever the custom table is updated
            // This ensures the summary shows current companies and charter selections
            if (typeof regenerateSummaryContent === 'function') {
                setTimeout(() => regenerateSummaryContent(), 10);
            }
            
            // Custom table is not sortable - users can drag to reorder companies manually
        }
        
        function updateCheckboxes() {
            const customCompanies = getCustomCompanies();
            // Only update main table checkboxes, not Countries & Companies filter checkboxes
            document.querySelectorAll('table .company-checkbox').forEach(checkbox => {
                const companyName = checkbox.dataset.company;
                checkbox.checked = customCompanies.includes(companyName);
            });
        }
        
        function updateControlButtons() {
            const customCompanies = getCustomCompanies();
            const isEmpty = customCompanies.length === 0;
            
            // Update Clear button
            const clearBtn = document.querySelector('.clear-btn');
            if (clearBtn) {
                clearBtn.disabled = isEmpty;
            }
            
            // Update Save button  
            const saveBtn = document.querySelector('.save-btn');
            if (saveBtn) {
                saveBtn.disabled = isEmpty;
            }
            
            // Update Share button
            const shareBtn = document.querySelector('.share-btn');
            if (shareBtn) {
                shareBtn.disabled = isEmpty;
            }
        }
        
        function updateDynamicCoverage() {
            const selectedCompanies = getCustomCompanies();
            const selectedCharters = getSelectedCharters();
            const companyData = ''' + self._get_company_data_js() + ''';
            
            // Calculate what buildings are already covered by selected companies and their active charters
            const coveredBuildings = new Set();
            selectedCompanies.forEach(companyName => {
                const company = companyData[companyName];
                if (company) {
                    // Add base buildings to covered set
                    if (company.building_types) {
                        company.building_types.forEach(building => {
                            coveredBuildings.add(building);
                        });
                    }
                    
                    // Add selected charter building to covered set
                    const selectedCharter = selectedCharters[companyName];
                    if (selectedCharter) {
                        coveredBuildings.add(selectedCharter);
                    }
                }
            });
            
            
            // Update all dynamic coverage cells
            const dynamicCells = document.querySelectorAll('.dynamic-coverage-column[data-company]');
            dynamicCells.forEach(cell => {
                const companyName = cell.getAttribute('data-company');
                const company = companyData[companyName];
                
                if (!company) {
                    cell.textContent = '0';
                    cell.style.color = '#6b7280';
                    return;
                }
                
                // Start at 0 for each company
                let companyScore = 0;
                let hasUsedCharter = false;
                
                // Get enabled buildings to filter calculations
                const enabledBuildings = getEnabledBuildings();
                
                // Process base buildings first
                if (company.building_types) {
                    company.building_types.forEach(building => {
                        // Only consider buildings that are enabled by user filters
                        if (!enabledBuildings.includes(building)) return;
                        
                        // If a base building is NOT covered by any buildings or active charters from selected companies
                        if (!coveredBuildings.has(building)) {
                            companyScore += 1;
                        }
                    });
                }
                
                // Process potential charters
                if (company.extension_building_types && company.extension_building_types.length > 0) {
                    company.extension_building_types.forEach(charter => {
                        // Only consider buildings that are enabled by user filters
                        if (!enabledBuildings.includes(charter)) return;
                        
                        // If a potential charter is NOT covered by any buildings or active charters from selected companies
                        // AND we have not used a charter for this company yet
                        if (!coveredBuildings.has(charter) && !hasUsedCharter) {
                            companyScore += 1;
                            hasUsedCharter = true;
                        }
                    });
                }
                
                
                // Display the score
                cell.textContent = companyScore.toString();
                
                // Color coding
                if (companyScore > 0) {
                    cell.style.color = '#16a34a'; // Green for positive value
                    cell.style.fontWeight = 'bold';
                } else {
                    cell.style.color = '#dc2626'; // Red for no value
                    cell.style.fontWeight = 'normal';
                }
            });
        }
        
        // Drag and Drop functionality for reordering companies
        let draggedElement = null;
        
        function dragStart(event) {
            draggedElement = event.target.closest('tr');
            draggedElement.style.opacity = '0.5';
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('text/html', draggedElement.outerHTML);
        }
        
        function dragOver(event) {
            event.preventDefault();
            event.dataTransfer.dropEffect = 'move';
            const targetRow = event.target.closest('tr');
            if (targetRow && targetRow !== draggedElement) {
                targetRow.style.borderTop = '2px solid #8b6914';
            }
        }
        
        function dragDrop(event) {
            event.preventDefault();
            const targetRow = event.target.closest('tr');
            if (targetRow && targetRow !== draggedElement) {
                const customCompanies = getCustomCompanies();
                const draggedCompany = draggedElement.dataset.company;
                const targetCompany = targetRow.dataset.company;
                
                const draggedIndex = customCompanies.indexOf(draggedCompany);
                const targetIndex = customCompanies.indexOf(targetCompany);
                
                // Remove dragged company and insert at target position
                customCompanies.splice(draggedIndex, 1);
                customCompanies.splice(targetIndex, 0, draggedCompany);
                
                saveCustomCompanies(customCompanies);
                updateCustomTable();
            }
            clearDragStyles();
        }
        
        function dragEnd(event) {
            clearDragStyles();
        }
        
        function clearDragStyles() {
            if (draggedElement) {
                draggedElement.style.opacity = '1';
                draggedElement = null;
            }
            document.querySelectorAll('tr').forEach(row => {
                row.style.borderTop = '';
            });
        }
        
        // Selection Management Functions
        function clearSelection() {
            const customCompanies = getCustomCompanies();
            if (customCompanies.length === 0) return; // Don't do anything if already empty
            
            if (confirm('Are you sure you want to clear all selected companies?')) {
                localStorage.removeItem(STORAGE_KEY);
                localStorage.removeItem(CHARTER_STORAGE_KEY);
                updateCustomTable();
                updateCheckboxes();
                updateControlButtons();
                updateDynamicCoverage();
                updateBuildingTableCharters();
            }
        }
        
        function saveSelection() {
            const customCompanies = getCustomCompanies();
            if (customCompanies.length === 0) return; // Don't do anything if empty
            
            const selectedCharters = getSelectedCharters();
            
            // Create selection data object
            const selectionData = {
                version: "1.0",
                timestamp: new Date().toISOString(),
                companies: customCompanies,
                charters: selectedCharters,
                meta: {
                    totalCompanies: customCompanies.length,
                    selectedCharters: Object.keys(selectedCharters).length
                }
            };
            
            // Create and download JSON file
            const dataStr = JSON.stringify(selectionData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            // Generate smart filename based on most common country
            // Use the same companyData that's available globally
            let countryCount = {};
            let hasNonBasic = false;
            
            customCompanies.forEach(companyName => {
                const company = companyData[companyName];
                if (!company) return;
                
                if (!companyName.startsWith('company_basic_')) {
                    hasNonBasic = true;
                    const country = company.country || 'unknown';
                    countryCount[country] = (countryCount[country] || 0) + 1;
                }
            });
            
            let baseFilename;
            if (!hasNonBasic) {
                baseFilename = 'basic';
            } else {
                // Find most common country
                const sortedCountries = Object.entries(countryCount).sort((a, b) => b[1] - a[1]);
                if (sortedCountries.length > 0 && sortedCountries[0][1] >= 3) {
                    // Use country name if 3+ companies from same country
                    const countryCode = sortedCountries[0][0];
                    // Convert country code to readable name
                    const countryNames = ''' + str({
                        'USA': 'usa', 'GBR': 'britain', 'DEU': 'germany', 'FRA': 'france', 
                        'RUS': 'russia', 'JAP': 'japan', 'CHI': 'china', 'BIC': 'india',
                        'AUS': 'austria-hungary', 'ITA': 'italy', 'SPA': 'spain', 'MEX': 'mexico',
                        'BRZ': 'brazil', 'ARG': 'argentina', 'CAN': 'canada', 'TUR': 'turkey',
                        'EGY': 'egypt', 'PER': 'persia', 'NET': 'netherlands', 'BEL': 'belgium',
                        'SWE': 'sweden', 'NOR': 'norway', 'DEN': 'denmark', 'FIN': 'finland',
                        'POL': 'poland', 'ROM': 'romania', 'SER': 'serbia', 'GRE': 'greece'
                    }).replace("'", '"') + ''';
                    baseFilename = countryNames[countryCode] || 'companies';
                } else {
                    baseFilename = 'companies';
                }
            }
            
            // Add date-time suffix
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            
            link.download = `${baseFilename}-${year}${month}${day}-${hours}${minutes}${seconds}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
        
        function triggerImportSelection() {
            document.getElementById('import-file-input').click();
        }
        
        function importSelection(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const selectionData = JSON.parse(e.target.result);
                    
                    // Validate the JSON structure
                    if (!selectionData.companies || !Array.isArray(selectionData.companies)) {
                        throw new Error('Invalid selection file format: missing companies array');
                    }
                    
                    // Validate that companies exist in our data
                    const validCompanies = selectionData.companies.filter(companyName => {
                        return companyData.hasOwnProperty(companyName);
                    });
                    
                    if (validCompanies.length === 0) {
                        alert('No valid companies found in the selection file.');
                        return;
                    }
                    
                    // Import the selection
                    saveCustomCompanies(validCompanies);
                    
                    // Import charters if they exist
                    if (selectionData.charters && typeof selectionData.charters === 'object') {
                        const validCharters = {};
                        for (const [companyName, charter] of Object.entries(selectionData.charters)) {
                            if (validCompanies.includes(companyName)) {
                                validCharters[companyName] = charter;
                            }
                        }
                        saveSelectedCharters(validCharters);
                    }
                    
                    // Update UI
                    updateCustomTable();
                    updateCheckboxes();
                    updateControlButtons();
                    updateDynamicCoverage();
                    updateBuildingTableCharters();
                    
                    const importedCount = validCompanies.length;
                    const totalCount = selectionData.companies.length;
                    
                    // Silent import - no popup needed for successful imports
                    // Only show alert if there were issues
                    if (importedCount < totalCount) {
                        alert(`Imported ${importedCount} out of ${totalCount} companies. ${totalCount - importedCount} companies were not found in the current data.`);
                    }
                    
                } catch (error) {
                    alert('Error importing selection: ' + error.message);
                }
            };
            reader.readAsText(file);
            
            // Reset the file input
            event.target.value = '';
        }

        function copyToClipboard() {
            const textArea = document.getElementById('copy-text');
            if (textArea) {
                textArea.select();
                textArea.setSelectionRange(0, 99999); // For mobile devices
                
                try {
                    document.execCommand('copy');
                    
                    // Visual feedback
                    const button = event.target;
                    const originalText = button.textContent;
                    button.textContent = 'Copied!';
                    button.style.background = '#28a745';
                    
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.style.background = '#4a7c59';
                    }, 1500);
                } catch (err) {
                    console.error('Failed to copy text: ', err);
                    // Fallback: select text for manual copy
                    textArea.focus();
                    textArea.select();
                }
            }
        }
        
        // Initialize sortable tables when DOM is ready
        // Load companies and charters from URL parameters
        function loadFromURL() {
            const urlParams = new URLSearchParams(window.location.search);
            // Support both short (c, ch) and long (companies, charters) parameter names for backwards compatibility
            const companiesParam = urlParams.get('c') || urlParams.get('companies');
            const chartersParam = urlParams.get('ch') || urlParams.get('charters');
            
            if (companiesParam) {
                const companyItems = companiesParam.split(',').map(item => item.trim());
                const validCompanies = [];
                
                // Find companies by ID (new format) or legacy name/key (old format)
                companyItems.forEach(nameOrKeyOrId => {
                    let foundCompany = null;
                    
                    // First try to parse as ID (numeric)
                    if (/^\d+$/.test(nameOrKeyOrId)) {
                        const id = parseInt(nameOrKeyOrId);
                        const companyKey = idToCompany[id];
                        if (companyKey && companyData[companyKey]) {
                            foundCompany = companyKey;
                        }
                    } else {
                        // Fallback to legacy name/key lookup
                        for (const [companyKey, company] of Object.entries(companyData)) {
                            const cleanKey = companyKey.replace('company_', '').toLowerCase();
                            if (cleanKey === nameOrKeyOrId.toLowerCase() || 
                                company.name.toLowerCase() === nameOrKeyOrId.toLowerCase()) {
                                foundCompany = companyKey;
                                break;
                            }
                        }
                    }
                    
                    if (foundCompany) {
                        validCompanies.push(foundCompany);
                    } else {
                        console.warn(`Company not found: ${nameOrKeyOrId}`);
                    }
                });
                
                if (validCompanies.length > 0) {
                    // Save the companies
                    saveCustomCompanies(validCompanies);
                    
                    // Load charters if provided
                    if (chartersParam) {
                        const charterEntries = chartersParam.split(',').map(entry => entry.trim());
                        const validCharters = {};
                        
                        charterEntries.forEach(entry => {
                            const [companyItem, buildingItem] = entry.split(':');
                            if (companyItem && buildingItem) {
                                // Find the company by ID (new) or name (legacy)
                                let foundCompany = null;
                                if (/^\d+$/.test(companyItem)) {
                                    // Parse as company ID
                                    const companyId = parseInt(companyItem);
                                    foundCompany = idToCompany[companyId];
                                } else {
                                    // Legacy name/key lookup
                                    for (const [companyKey, company] of Object.entries(companyData)) {
                                        const cleanKey = companyKey.replace('company_', '').toLowerCase();
                                        if (cleanKey === companyItem.toLowerCase() || 
                                            company.name.toLowerCase() === companyItem.toLowerCase()) {
                                            foundCompany = companyKey;
                                            break;
                                        }
                                    }
                                }
                                
                                // Find the building by ID (new) or name (legacy)
                                let foundBuilding = null;
                                if (/^\d+$/.test(buildingItem)) {
                                    // Parse as building ID
                                    const buildingId = parseInt(buildingItem);
                                    foundBuilding = idToBuilding[buildingId];
                                } else {
                                    // Legacy building name lookup (handled below)
                                }
                                
                                if (foundCompany && validCompanies.includes(foundCompany)) {
                                    const company = companyData[foundCompany];
                                    
                                    // Handle building lookup - foundBuilding is already set for ID format
                                    if (!foundBuilding) {
                                        // Legacy building name lookup
                                        const buildingKey = buildingItem.startsWith('building_') ? buildingItem : `building_${buildingItem}`;
                                        if (company.industry_charters.includes(buildingKey)) {
                                            foundBuilding = buildingKey;
                                        }
                                    }
                                    
                                    // Verify the building is valid for this company
                                    if (foundBuilding && company.industry_charters.includes(foundBuilding)) {
                                        validCharters[foundCompany] = foundBuilding;
                                    }
                                }
                            }
                        });
                        
                        if (Object.keys(validCharters).length > 0) {
                            saveSelectedCharters(validCharters);
                        }
                    }
                    
                    console.log(`Loaded ${validCompanies.length} companies from URL`);
                }
            }
        }
        
        // Company and building ID mappings for shorter URLs
        const companyIdMap = {
            {company_mappings}
        };
        
        const buildingIdMap = {
            {building_mappings}
        };
        
        // Reverse mappings for URL parsing
        const idToCompany = Object.fromEntries(Object.entries(companyIdMap).map(([k, v]) => [v, k]));
        const idToBuilding = Object.fromEntries(Object.entries(buildingIdMap).map(([k, v]) => [v, k]));
        
        // Generate shareable URL with current selection
        function generateShareURL(silent = false, event = null) {
            const customCompanies = getCustomCompanies();
            const selectedCharters = getSelectedCharters();
            
            if (customCompanies.length === 0) {
                if (!silent) {
                    alert('No companies selected to share');
                }
                return null;
            }
            
            const baseURL = 'https://alcaras.github.io/v3co/';
            const urlParams = [];
            
            // Add companies using IDs for shorter URLs
            const companyIds = customCompanies.map(companyKey => companyIdMap[companyKey]).filter(id => id !== undefined);
            urlParams.push(`c=${companyIds.join(',')}`);
            
            // Add charters using IDs for shorter URLs
            const charterEntries = [];
            Object.entries(selectedCharters).forEach(([companyKey, buildingKey]) => {
                const companyId = companyIdMap[companyKey];
                const buildingId = buildingIdMap[buildingKey];
                if (companyId !== undefined && buildingId !== undefined) {
                    charterEntries.push(`${companyId}:${buildingId}`);
                }
            });
            
            if (charterEntries.length > 0) {
                urlParams.push(`ch=${charterEntries.join(',')}`);
            }
            
            const shareURL = `${baseURL}?${urlParams.join('&')}`;
            
            // If silent mode, just return the URL
            if (silent) {
                return shareURL;
            }
            
            // Copy to clipboard and show button feedback
            navigator.clipboard.writeText(shareURL).then(() => {
                // Show button feedback similar to copy button
                const button = event && event.target ? event.target : document.querySelector('.share-btn');
                if (button) {
                    const originalText = button.innerHTML;
                    const originalBackground = button.style.background;
                    button.innerHTML = '✓ Link Copied!';
                    button.style.background = '#28a745';
                    
                    setTimeout(() => {
                        button.innerHTML = originalText;
                        button.style.background = originalBackground;
                    }, 2000);
                }
            }).catch(() => {
                // Fallback - show the URL
                prompt('Share URL (copy this):', shareURL);
            });
            
            return shareURL;
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            var tables = document.querySelectorAll('table.sortable');
            tables.forEach(makeSortable);
            
            // Initialize country count but NOT continent checkboxes (let them start checked)
            updateCountryCount();
            // updateContinentCheckboxes(); // Disabled to let checkboxes start checked
            
            // Load from URL first, then update UI
            loadFromURL();
            updateCustomTable();
            updateCheckboxes();
            updateControlButtons();
            updateDynamicCoverage();
            updateMainBuildingHeaders();
            updateBuildingTableCharters();
            updateBuildingCount();
            
        });
        
        // Console helper functions for debugging
        window.debugSelectAllCompanies = function() {
            const allCompanies = Object.keys(companyData);
            console.log(`Selecting all ${allCompanies.length} companies...`);
            
            allCompanies.forEach(companyName => {
                const checkbox = document.querySelector(`input[data-company="${companyName}"]`);
                if (checkbox && !checkbox.checked) {
                    checkbox.checked = true;
                    toggleCompanySelection(companyName);
                }
            });
            
            console.log('✅ All companies selected');
        };
        
        // Building short forms mapping (global scope for use in summary functions)
        const buildingShortForms = {
            'building_coal_mine': 'Coal',
            'building_fishing_wharf': 'Fish',
            'building_gold_mine': 'Gold',
            'building_iron_mine': 'Iron',
            'building_lead_mine': 'Lead',
            'building_logging_camp': 'Wood',
            'building_oil_rig': 'Oil',
            'building_rubber_plantation': 'Rubber',
            'building_sulfur_mine': 'Sulfur',
            'building_whaling_station': 'Whaling',
            'building_arms_industry': 'Arms',
            'building_artillery_foundries': 'Artillery',
            'building_automotive_industry': 'Auto',
            'building_electrics_industry': 'Electric',
            'building_explosives_factory': 'Explosives',
            'building_chemical_plants': 'Fertilizer',
            'building_food_industry': 'Food',
            'building_furniture_manufacturies': 'Furniture',
            'building_glassworks': 'Glass',
            'building_military_shipyards': 'Mil. Shipyards',
            'building_motor_industry': 'Motors',
            'building_munition_plants': 'Munitions',
            'building_paper_mills': 'Paper',
            'building_shipyards': 'Shipyards',
            'building_steel_mills': 'Steel',
            'building_synthetics_plants': 'Synthetics',
            'building_textile_mills': 'Textiles',
            'building_tooling_workshops': 'Tools',
            'building_port': 'Port',
            'building_railway': 'Railway',
            'building_trade_center': 'Trade',
            'building_power_plant': 'Power',
            'building_arts_academy': 'Arts',
            'building_maize_farm': 'Maize',
            'building_millet_farm': 'Millet',
            'building_rice_farm': 'Rice',
            'building_rye_farm': 'Rye',
            'building_wheat_farm': 'Wheat',
            'building_vineyard_plantation': 'Wine',
            'building_banana_plantation': 'Banana',
            'building_coffee_plantation': 'Coffee',
            'building_cotton_plantation': 'Cotton',
            'building_dye_plantation': 'Dye',
            'building_opium_plantation': 'Opium',
            'building_silk_plantation': 'Silk',
            'building_sugar_plantation': 'Sugar',
            'building_tea_plantation': 'Tea',
            'building_tobacco_plantation': 'Tobacco',
            'building_livestock_ranch': 'Livestock'
        };
        
        // Set Cover Optimization - Proper greedy algorithm for company selection
        // This is much more appropriate than LP for this specific problem
        function solveSetCover(universe, sets, maxSets) {
            // universe: array of items to cover (target buildings)
            // sets: array of {id, items, weight} where items is array of covered universe items
            // maxSets: maximum number of sets to select
            // Returns: {selected: [setIds], coverage: number, items: [covered items]}
            
            if (sets.length === 0 || universe.length === 0) {
                return { selected: [], coverage: 0, items: [] };
            }
            
            const uncovered = new Set(universe);
            const selected = [];
            const coveredItems = new Set();
            
            // Greedy: repeatedly pick the set that covers the most uncovered items per unit weight
            while (selected.length < maxSets && uncovered.size > 0) {
                let bestSet = null;
                let bestEfficiency = -1;
                
                for (const set of sets) {
                    // Skip if already selected
                    if (selected.find(s => s.id === set.id)) continue;
                    
                    // Calculate how many new items this set would cover
                    const newItems = set.items.filter(item => uncovered.has(item));
                    if (newItems.length === 0) continue;
                    
                    // Efficiency = new items covered per unit weight
                    const efficiency = newItems.length / (set.weight || 1);
                    
                    if (efficiency > bestEfficiency) {
                        bestEfficiency = efficiency;
                        bestSet = { ...set, newItems };
                    }
                }
                
                if (!bestSet) break; // No more useful sets
                
                // Select the best set
                selected.push(bestSet);
                bestSet.newItems.forEach(item => {
                    uncovered.delete(item);
                    coveredItems.add(item);
                });
            }
            
            return {
                selected: selected,
                coverage: coveredItems.size,
                items: Array.from(coveredItems),
                coveragePercent: Math.round((coveredItems.size / universe.length) * 100)
            };
        }

        // Optimization Feature Functions
        let optimizationResults = null;
        
        function optimizeSelection() {
            const enabledBuildings = getEnabledBuildings();
            const selectedCompanies = getCustomCompanies();
            const selectedCharters = getSelectedCharters();
            const enabledCompanies = getEnabledCompanies();
            
            // Get company limit from dropdown
            const companyLimit = parseInt(document.getElementById('company-limit-dropdown').value);
            
            // Check if any buildings are selected
            if (enabledBuildings.length === 0) {
                alert('Please select at least one building to optimize for.');
                return;
            }
            
            // Show modal with loading status
            document.getElementById('optimizationModal').style.display = 'block';
            document.getElementById('optimizationStatus').textContent = `Calculating optimal company selection (max ${companyLimit} companies)...`;
            document.getElementById('optimizationResults').innerHTML = '';
            
            // Run optimization with a small delay to let UI update
            setTimeout(() => {
                const results = runOptimization(enabledBuildings, selectedCompanies, selectedCharters, enabledCompanies, companyLimit);
                displayOptimizationResults(results);
            }, 100);
        }
        
        function runOptimization(targetBuildings, existingCompanies, existingCharters, enabledCompanies, companyLimit = 7) {
            const MAX_COMPANIES = companyLimit;
            // USE LIVE GLOBAL companyData instead of embedded data
            // The global companyData has complete building information with building_types and extension_building_types
            
            // Special companies that don't count against the limit
            const specialCompanies = ['company_panama_company', 'company_suez_company'];
            
            // Filter out special companies from existing selection
            const regularExisting = existingCompanies.filter(c => !specialCompanies.includes(c));
            const specialExisting = existingCompanies.filter(c => specialCompanies.includes(c));
            
            // Calculate remaining slots
            const remainingSlots = MAX_COMPANIES - regularExisting.length;
            
            if (remainingSlots <= 0) {
                return {
                    success: false,
                    message: `You already have ${MAX_COMPANIES} companies selected. Remove some to optimize.`,
                    existingCompanies: regularExisting,
                    newCompanies: [],
                    coverage: calculateCoverage(targetBuildings, existingCompanies, existingCharters)
                };
            }
            
            // Use Linear Programming to find optimal selection
            try {
                const lpResult = solveLinearProgram(targetBuildings, regularExisting, existingCharters, enabledCompanies, remainingSlots);
                
                if (!lpResult.success) {
                    return {
                        success: false,
                        message: lpResult.message || 'Optimization failed',
                        existingCompanies: regularExisting,
                        newCompanies: [],
                        coverage: calculateCoverage(targetBuildings, existingCompanies, existingCharters)
                    };
                }
                
                // Check if we should add Panama or Suez
                const finalRecommendations = [];
                const allSelectedBuildings = new Set();
                regularExisting.forEach(name => {
                    const company = companyData[name];
                    if (company) {
                        (company.building_types || []).forEach(b => allSelectedBuildings.add(b));
                        if (existingCharters[name]) allSelectedBuildings.add(existingCharters[name]);
                    }
                });
                lpResult.newCompanies.forEach(rec => {
                    rec.coverage.forEach(b => allSelectedBuildings.add(b));
                });
                
                specialCompanies.forEach(specialName => {
                    if (!specialExisting.includes(specialName)) {
                        const special = companyData[specialName];
                        if (special) {
                            const newCoverage = (special.building_types || []).filter(b => 
                                targetBuildings.includes(b) && !allSelectedBuildings.has(b)
                            );
                            if (newCoverage.length > 0) {
                                finalRecommendations.push({
                                    name: specialName,
                                    isSpecial: true,
                                    coverage: special.building_types || []
                                });
                            }
                        }
                    }
                });
                
                // Calculate coverage INCLUDING special recommendations
                const allCompanies = [
                    ...regularExisting, 
                    ...lpResult.newCompanies.map(c => c.name),
                    ...finalRecommendations.map(r => r.name) // Include special companies!
                ];
                const allCharters = {
                    ...existingCharters, 
                    ...Object.fromEntries(lpResult.newCompanies.filter(c => c.charter).map(c => [c.name, c.charter]))
                };
                
                return {
                    success: true,
                    existingCompanies: regularExisting,
                    existingCharters: existingCharters,
                    newCompanies: lpResult.newCompanies,
                    specialRecommendations: finalRecommendations,
                    coverage: calculateDetailedCoverage(targetBuildings, allCompanies, allCharters)
                };
            } catch (error) {
                console.error('Optimization error:', error);
                return {
                    success: false,
                    message: 'Optimization failed: ' + error.message,
                    existingCompanies: regularExisting,
                    newCompanies: [],
                    coverage: calculateCoverage(targetBuildings, existingCompanies, existingCharters)
                };
            }
        }
        
        function solveCorrectedYALPS(candidates, remainingSlots, uncoveredBuildings) {
            // WORKING SET COVER YALPS: True set cover without double-counting
            console.log('🔍 solveCorrectedYALPS started with:', candidates.length, 'candidates,', remainingSlots, 'slots');
            console.log('🔍 Sample candidates:', candidates.slice(0, 3).map(c => ({id: c.id, buildings: c.buildings.length})));
            
            if (candidates.length === 0) {
                console.log('❌ No candidates provided to YALPS solver');
                return {
                    status: 'optimal',
                    result: 0,
                    variables: []
                };
            }
            
            // Get all buildings that could be covered
            const allBuildings = new Set();
            candidates.forEach(candidate => {
                candidate.buildings.forEach(b => allBuildings.add(b));
            });
            const buildingList = Array.from(allBuildings);
            
            // CORRECT SET COVER FORMULATION
            const model = {
                direction: 'maximize',
                objective: 'unique_buildings',
                constraints: {
                    max_regular_companies: { max: remainingSlots }
                },
                variables: {},
                binaries: []
            };
            
            console.log('🔧 Building YALPS model for', buildingList.length, 'buildings,', remainingSlots, 'company slots');
            
            // Building coverage variables: building_company pairs
            // covers_building_company = 1 if company covers that specific building
            buildingList.forEach(building => {
                candidates.forEach(candidate => {
                    if (candidate.buildings.includes(building)) {
                        const coverageVar = `covers_${building}_${candidate.id}`;
                        model.variables[coverageVar] = {
                            unique_buildings: 1  // Each building-company pair contributes 1
                        };
                        model.binaries.push(coverageVar);
                    }
                });
            });
            
            // Company selection variables
            candidates.forEach(candidate => {
                const companyVar = `select_${candidate.id}`;
                // MATCH NODE.JS: Companies DON'T contribute to objective directly
                model.variables[companyVar] = {};
                
                // Special companies (Panama/Suez) don't count against the company limit
                if (!candidate.isSpecial) {
                    model.variables[companyVar].max_regular_companies = 1;
                }
                
                model.binaries.push(companyVar);
            });
            
            // Each building coverage is counted at most once in the objective
            buildingList.forEach(building => {
                const constraint = `unique_cover_${building}`;
                model.constraints[constraint] = { max: 1 };
                
                candidates.forEach(candidate => {
                    if (candidate.buildings.includes(building)) {
                        const coverageVar = `covers_${building}_${candidate.id}`;
                        model.variables[coverageVar][constraint] = 1;
                    }
                });
            });
            
            // Link coverage to company selection: can only cover building if company is selected
            buildingList.forEach(building => {
                candidates.forEach(candidate => {
                    if (candidate.buildings.includes(building)) {
                        const constraint = `link_${building}_${candidate.id}`;
                        const coverageVar = `covers_${building}_${candidate.id}`;
                        const companyVar = `select_${candidate.id}`;
                        
                        model.constraints[constraint] = { max: 0 };
                        model.variables[coverageVar][constraint] = 1;
                        model.variables[companyVar][constraint] = -1; // If company selected, coverage can be 1
                    }
                });
            });
            
            // Mutual exclusion constraints
            const companyGroups = {};
            candidates.forEach(candidate => {
                if (!companyGroups[candidate.name]) {
                    companyGroups[candidate.name] = [];
                }
                companyGroups[candidate.name].push(candidate.id);
            });
            
            let exclusionCount = 0;
            Object.keys(companyGroups).forEach(companyName => {
                if (companyGroups[companyName].length > 1) {
                    const constraint = `exclusive_${companyName}`;
                    model.constraints[constraint] = { max: 1 };
                    exclusionCount++;
                    
                    companyGroups[companyName].forEach(candidateId => {
                        model.variables[`select_${candidateId}`][constraint] = 1;
                    });
                }
            });
            console.log(`🔧 Added ${exclusionCount} mutual exclusion constraints`);
            
            // USE REAL YALPS: Always use YALPS solver
            console.log('🔧 Calling real YALPS solver with model:', Object.keys(model.variables).length, 'variables,', Object.keys(model.constraints).length, 'constraints');
            
            // ALWAYS USE YALPS - NO FALLBACKS
            const yalpsResult = window.YALPS.solve(model);
            console.log('📋 Real YALPS result:', yalpsResult);
            
            // Extract selected companies from YALPS result
            // YALPS returns variables as an array of [name, value] pairs
            const selectedCandidates = [];
            const variablesArray = Array.isArray(yalpsResult.variables) 
                ? yalpsResult.variables 
                : Object.entries(yalpsResult.variables || {});
            
            console.log('🔍 Parsing YALPS variables:', variablesArray.length, 'total');
            
            // Process ALL variables - both select_ and covers_ might be present
            const selectedCompanyIds = new Set();
            
            variablesArray.forEach(([varName, value]) => {
                if (value > 0.5) {
                    if (varName.startsWith('select_')) {
                        // Direct company selection
                        const candidateId = varName.replace('select_', '');
                        selectedCompanyIds.add(candidateId);
                        console.log('  ✓ Found select variable:', candidateId);
                    } else if (varName.startsWith('covers_')) {
                        // Extract company from coverage variable
                        const parts = varName.split('_');
                        // Format: covers_building_XXX_company_YYY
                        // Find where 'company' starts in the parts
                        const companyIndex = parts.indexOf('company');
                        if (companyIndex > 0) {
                            const companyPart = parts.slice(companyIndex).join('_');
                            selectedCompanyIds.add(companyPart);
                            console.log('  ✓ Found coverage for:', companyPart);
                        } else {
                            // Try alternative: everything after first 3 parts
                            const companyPart = parts.slice(3).join('_');
                            if (companyPart) {
                                selectedCompanyIds.add(companyPart);
                                console.log('  ✓ Found coverage for (alt):', companyPart);
                            }
                        }
                    }
                }
            });
            
            console.log('🔍 Unique company IDs found:', selectedCompanyIds.size);
            
            // Find matching candidates and deduplicate by company name
            const companiesAdded = new Set();
            selectedCompanyIds.forEach(companyId => {
                const candidate = candidates.find(c => c.id === companyId);
                if (candidate) {
                    // Only add one variant per company (prefer charter over base)
                    if (!companiesAdded.has(candidate.name)) {
                        selectedCandidates.push(candidate);
                        companiesAdded.add(candidate.name);
                    } else {
                        // Check if this is a charter variant that should replace base
                        const existingIndex = selectedCandidates.findIndex(c => c.name === candidate.name);
                        if (existingIndex >= 0 && candidate.charter && !selectedCandidates[existingIndex].charter) {
                            console.log(`  ↔️ Replacing base with charter for ${candidate.name}`);
                            selectedCandidates[existingIndex] = candidate;
                        }
                    }
                } else {
                    console.warn('  ⚠️ Could not find candidate for ID:', companyId);
                }
            });
            
            // Calculate total coverage
            const coveredBuildings = new Set();
            selectedCandidates.forEach(c => c.buildings.forEach(b => coveredBuildings.add(b)));
            
            return {
                status: yalpsResult.status || 'optimal',
                result: coveredBuildings.size,
                variables: variablesArray,
                selectedCandidates: selectedCandidates
            };
        }

        function solveSetCoverDirectly(candidates, remainingSlots, buildingList) {
            // Implement the working set cover algorithm that achieved 30 buildings
            // This replicates the YALPS linear programming logic without using the fake YALPS
            
            console.log('🔍 solveSetCoverDirectly: checking candidate name format');
            console.log('First 3 candidate names:', candidates.slice(0, 3).map(c => c.name));
            
            const specialCompanies = ['company_panama_company', 'company_suez_company'];
            
            // Separate special and regular candidates  
            // FIX: HTML candidates actually DO use full names (company_panama_company)
            const specialCandidates = candidates.filter(c => specialCompanies.includes(c.name));
            const regularCandidates = candidates.filter(c => !specialCompanies.includes(c.name));
            
            console.log('🔍 Special candidates found:', specialCandidates.length);
            console.log('🔍 Regular candidates found:', regularCandidates.length);
            
            // Always include best special companies (they're FREE)
            const selectedCompanies = [];
            const coveredBuildings = new Set();
            
            // Add best special companies (once per company, not per variant)
            const processedSpecialCompanies = new Set();
            specialCandidates.forEach(specialCandidate => {
                const companyName = specialCandidate.name;
                
                // Skip if we already processed this company
                if (processedSpecialCompanies.has(companyName)) {
                    return;
                }
                processedSpecialCompanies.add(companyName);
                
                // Find all variants of this company
                const companyVariants = specialCandidates.filter(c => c.name === companyName);
                
                if (companyVariants.length > 0) {
                    // Pick the variant with most buildings  
                    const bestVariant = companyVariants.reduce((best, current) => 
                        current.buildings.length > best.buildings.length ? current : best
                    );
                    
                    selectedCompanies.push(bestVariant);
                    bestVariant.buildings.forEach(b => coveredBuildings.add(b));
                }
            });
            
            // Greedily select regular companies to maximize NEW building coverage
            const companyGroups = {};
            regularCandidates.forEach(candidate => {
                if (!companyGroups[candidate.name]) companyGroups[candidate.name] = [];
                companyGroups[candidate.name].push(candidate);
            });
            
            let regularCount = 0;
            const maxRegular = remainingSlots;
            
            while (regularCount < maxRegular && Object.keys(companyGroups).length > 0) {
                let bestCompany = null;
                let bestCandidate = null;
                let bestNewBuildings = 0;
                
                // Find company variant that adds most NEW buildings
                Object.entries(companyGroups).forEach(([companyName, variants]) => {
                    variants.forEach(candidate => {
                        // Filter for relevant buildings that are in our target set and not already covered
                        const newBuildings = candidate.buildings.filter(b => {
                            const cleanBuilding = b.replace('building_', '');
                            return buildingList.includes(cleanBuilding) && !coveredBuildings.has(b);
                        });
                        if (newBuildings.length > bestNewBuildings) {
                            bestNewBuildings = newBuildings.length;
                            bestCandidate = candidate;
                            bestCompany = companyName;
                        }
                    });
                });
                
                if (!bestCandidate || bestNewBuildings === 0) break; // No more improvements
                
                selectedCompanies.push(bestCandidate);
                bestCandidate.buildings.forEach(b => coveredBuildings.add(b));
                delete companyGroups[bestCompany]; // Remove company group
                regularCount++;
            }
            
            // Format result to match expected format
            const resultVariables = [];
            selectedCompanies.forEach(company => {
                resultVariables.push([`select_${company.id}`, 1]);
            });
            
            return {
                status: 'optimal',
                result: coveredBuildings.size, // Actual unique buildings covered
                variables: resultVariables,
                selectedCandidates: selectedCompanies
            };
        }

        function solveLinearProgram(targetBuildings, existingCompanies, existingCharters, enabledCompanies, remainingSlots) {
            const companyData = ''' + self._get_company_data_js() + ''';
            const specialCompanies = ['company_panama_company', 'company_suez_company'];
            
            // Get buildings covered by existing selection
            const existingCoverage = new Set();
            existingCompanies.forEach(companyName => {
                const company = companyData[companyName];
                if (company) {
                    (company.building_types || []).forEach(b => existingCoverage.add(b));
                    if (existingCharters[companyName]) {
                        existingCoverage.add(existingCharters[companyName]);
                    }
                }
            });
            
            // Buildings we still need to cover
            const uncoveredBuildings = targetBuildings.filter(b => !existingCoverage.has(b));
            
            if (uncoveredBuildings.length === 0) {
                return {
                    success: true,
                    newCompanies: [],
                    message: 'All buildings already covered!'
                };
            }
            
            // Get candidate companies and their variants (with/without charters)
            const candidates = [];
            
            console.log('🔍 Starting candidate generation...');
            console.log('- Target buildings:', uncoveredBuildings.length, uncoveredBuildings.slice(0, 5));
            console.log('- Existing companies:', existingCompanies);
            console.log('- Special companies:', specialCompanies);
            console.log('- Enabled companies:', enabledCompanies.length);
            console.log('🔍 DEBUG: What companyData is runOptimization seeing?');
            console.log('- companyData type:', typeof companyData);
            console.log('- companyData keys count:', Object.keys(companyData).length);
            console.log('- Sample company:', companyData['company_ludwig_moser_and_sons']);
            
            let debugStats = {
                total: 0,
                skippedExisting: 0,
                skippedCountry: 0,
                skippedNoBuildings: 0,
                candidatesGenerated: 0
            };
            
            Object.keys(companyData).forEach(companyName => {
                debugStats.total++;
                
                // Skip if already selected (but NOT special companies - they should always be candidates)
                // Special companies (Panama/Suez) are free and should always be considered
                const isSpecial = specialCompanies.includes(companyName);
                if (existingCompanies.includes(companyName) && !isSpecial) {
                    debugStats.skippedExisting++;
                    if (debugStats.total <= 5) console.log(`❌ Skipping ${companyName}: already selected`);
                    return;
                }
                
                const company = companyData[companyName];
                
                // Apply company filter
                if (enabledCompanies.length > 0) {
                    if (!enabledCompanies.includes(companyName)) {
                        debugStats.skippedCountry++;
                        if (debugStats.total <= 5) console.log(`❌ Skipping ${companyName}: country ${company.country} not enabled`);
                        return;
                    }
                }
                
                // FIX: Use correct field names from global companyData
                // Global companyData uses building_types and extension_building_types  
                const baseBuildings = company.building_types || [];
                const charterBuildings = company.extension_building_types || [];
                
                if (debugStats.total <= 5) {
                    console.log(`🔍 Checking ${companyName}:`, {
                        country: company.country,
                        base_buildings: baseBuildings,
                        industry_charters: charterBuildings
                    });
                }
                
                // Check if company covers any uncovered buildings
                const allBuildings = new Set([...baseBuildings, ...charterBuildings]);
                const matchingBuildings = uncoveredBuildings.filter(b => allBuildings.has(b));
                
                if (debugStats.total <= 5) {
                    console.log(`  → All company buildings:`, Array.from(allBuildings));
                    console.log(`  → Matching buildings:`, matchingBuildings);
                }
                
                if (matchingBuildings.length === 0) {
                    debugStats.skippedNoBuildings++;
                    if (debugStats.total <= 5) console.log(`❌ Skipping ${companyName}: no matching buildings`);
                    return;
                }
                
                if (debugStats.total <= 5) console.log(`✅ ${companyName}: will generate candidates`);
                debugStats.candidatesGenerated++;
                
                // Add base company variant
                const relevantBaseBuildings = baseBuildings.filter(b => uncoveredBuildings.includes(b));
                if (relevantBaseBuildings.length > 0) {
                    candidates.push({
                        id: companyName + '_base',
                        name: companyName,
                        charter: null,
                        buildings: relevantBaseBuildings,
                        cost: isSpecial ? 0 : 1,  // Special companies are free
                        isBasic: companyName.startsWith('company_basic_'),
                        isSpecial: isSpecial
                    });
                }
                
                // Add charter variants
                charterBuildings.forEach(charter => {
                    const charterBuildingSet = [...baseBuildings];
                    if (uncoveredBuildings.includes(charter)) {
                        charterBuildingSet.push(charter);
                    }
                    const relevantBuildings = charterBuildingSet.filter(b => uncoveredBuildings.includes(b));
                    
                    if (relevantBuildings.length > 0) {
                        candidates.push({
                            id: companyName + '_charter_' + charter,
                            name: companyName,
                            charter: charter,
                            buildings: relevantBuildings,
                            cost: isSpecial ? 0 : 1,  // Special companies are free
                            isBasic: companyName.startsWith('company_basic_'),
                            isSpecial: isSpecial
                        });
                    }
                });
            });
            
            console.log('📊 Candidate Generation Summary:');
            console.log(`- Total companies: ${debugStats.total}`);
            console.log(`- Skipped existing/special: ${debugStats.skippedExisting}`);
            console.log(`- Skipped country filter: ${debugStats.skippedCountry}`);
            console.log(`- Skipped no buildings: ${debugStats.skippedNoBuildings}`);
            console.log(`- Companies processed: ${debugStats.candidatesGenerated}`);
            console.log(`- Final candidates generated: ${candidates.length}`);
            
            if (candidates.length === 0) {
                console.log('❌ NO CANDIDATES GENERATED!');
                console.log('🔍 Debug: Check if building names match between enabled buildings and company data');
                console.log('First 3 enabled buildings:', uncoveredBuildings.slice(0, 3));
                console.log('Sample company buildings:');
                const sampleCompanies = Object.keys(companyData).slice(0, 3);
                sampleCompanies.forEach(name => {
                    const company = companyData[name];
                    // FIX: Use correct field names from global companyData
                    const allBuildings = [...(company.building_types || []), ...(company.extension_building_types || [])];
                    console.log(`  ${name}: [${allBuildings.join(', ')}]`);
                });
                
                return {
                    success: false,
                    message: 'No companies available that cover the selected buildings.'
                };
            }
            
            // Set up FIXED Linear Programming model for real YALPS
            const model = {
                direction: "maximize",
                objective: "total_coverage",
                constraints: {
                    max_companies: { max: remainingSlots }
                },
                variables: {},
                binaries: []
            };
            
            // Add variables for each candidate with FIXED formulation
            candidates.forEach(candidate => {
                const relevantBuildings = candidate.buildings.filter(b => uncoveredBuildings.includes(b));
                
                model.variables[candidate.id] = {
                    max_companies: 1, // Each candidate costs 1 company slot
                    total_coverage: relevantBuildings.length // FIXED: Simple score = building count
                };
                
                model.binaries.push(candidate.id); // Binary variable
            });
            
            // Add mutual exclusion constraints (each company can only be selected once)
            const companyGroups = {};
            candidates.forEach(candidate => {
                if (!companyGroups[candidate.name]) {
                    companyGroups[candidate.name] = [];
                }
                companyGroups[candidate.name].push(candidate.id);
            });
            
            Object.keys(companyGroups).forEach(companyName => {
                if (companyGroups[companyName].length > 1) {
                    const constraintName = `exclusive_${companyName}`;
                    model.constraints[constraintName] = { max: 1 };
                    
                    companyGroups[companyName].forEach(candidateId => {
                        model.variables[candidateId][constraintName] = 1;
                    });
                }
            });
            
            // Use CORRECTED YALPS MAXIMUM COVERAGE formulation
            console.log('🚀 Calling solveCorrectedYALPS with:', candidates.length, 'candidates,', remainingSlots, 'slots,', uncoveredBuildings.length, 'uncovered buildings');
            const solution = solveCorrectedYALPS(candidates, remainingSlots, uncoveredBuildings);
            console.log('📋 YALPS solution result:', solution);
            
            if (solution.status !== 'optimal') {
                return {
                    success: false,
                    message: `Linear programming solver failed: ${solution.status}`
                };
            }
            
            // Extract selected companies from solution
            // FIX: Use selectedCandidates directly from our custom solver instead of parsing variables
            const selectedCandidates = solution.selectedCandidates || [];
            console.log('🔧 Selected candidates from solver:', selectedCandidates.length, 'companies');
            
            // Convert to expected format
            const finalSelection = selectedCandidates.map(candidate => ({
                name: candidate.name,
                charter: candidate.charter,
                coverage: candidate.buildings,
                score: candidate.buildings.filter(b => uncoveredBuildings.includes(b)).length
            }));
            
            return {
                success: true,
                newCompanies: finalSelection,
                optimalValue: solution.result
            };
        }
        
        function calculateCompanyScore(companyBuildings, targetBuildings, companyName) {
            let score = 0;
            
            // Count new buildings covered
            const newBuildings = Array.from(companyBuildings).filter(b => targetBuildings.includes(b));
            score += newBuildings.length * 100;
            
            // Penalty for basic companies (prefer named companies)
            if (companyName.startsWith('company_basic_')) {
                score -= 10;
            }
            
            // Bonus for companies with many charter options (flexibility)
            const company = companyData[companyName];
            if (company && company.extension_building_types) {
                score += Math.min(company.extension_building_types.length, 5) * 2;
            }
            
            return score;
        }
        
        function calculateCoverage(targetBuildings, companies, charters) {
            const covered = new Set();
            companies.forEach(companyName => {
                const company = companyData[companyName];
                if (company) {
                    (company.building_types || []).forEach(b => covered.add(b));
                    if (charters[companyName]) {
                        covered.add(charters[companyName]);
                    }
                }
            });
            
            const coveredTarget = targetBuildings.filter(b => covered.has(b));
            return {
                covered: coveredTarget.length,
                total: targetBuildings.length,
                percentage: Math.round((coveredTarget.length / targetBuildings.length) * 100)
            };
        }
        
        function calculateDetailedCoverage(targetBuildings, companies, charters) {
            const covered = new Set();
            companies.forEach(companyName => {
                const company = companyData[companyName];
                if (company) {
                    (company.building_types || []).forEach(b => covered.add(b));
                    if (charters[companyName]) {
                        covered.add(charters[companyName]);
                    }
                }
            });
            
            const coveredBuildings = targetBuildings.filter(b => covered.has(b));
            const uncoveredBuildings = targetBuildings.filter(b => !covered.has(b));
            
            return {
                covered: coveredBuildings.length,
                total: targetBuildings.length,
                percentage: Math.round((coveredBuildings.length / targetBuildings.length) * 100),
                coveredBuildings: coveredBuildings,
                uncoveredBuildings: uncoveredBuildings
            };
        }
        
        function displayOptimizationResults(results) {
            optimizationResults = results;
            
            const statusEl = document.getElementById('optimizationStatus');
            const resultsEl = document.getElementById('optimizationResults');
            
            if (!results.success) {
                statusEl.textContent = results.message;
                statusEl.style.color = '#dc3545';
                resultsEl.innerHTML = '';
                return;
            }
            
            statusEl.textContent = 'Optimization complete!';
            statusEl.style.color = '#28a745';
            
            let html = '<div class="optimization-stats">';
            html += '<div class="optimization-stat">';
            html += '<div class="optimization-stat-value">' + results.coverage.percentage + '%</div>';
            html += '<div class="optimization-stat-label">Building Coverage</div>';
            html += '</div>';
            html += '<div class="optimization-stat">';
            html += '<div class="optimization-stat-value">' + results.coverage.covered + '/' + results.coverage.total + '</div>';
            html += '<div class="optimization-stat-label">Buildings Covered</div>';
            html += '</div>';
            html += '<div class="optimization-stat">';
            const totalCompanies = results.existingCompanies.length + results.newCompanies.length;
            html += '<div class="optimization-stat-value">' + totalCompanies + '/7</div>';
            html += '<div class="optimization-stat-label">Companies Used</div>';
            html += '</div>';
            html += '</div>';
            
            // Show existing companies
            if (results.existingCompanies.length > 0) {
                html += '<h3>Your Selected Companies (Kept)</h3>';
                html += '<div class="optimization-results">';
                results.existingCompanies.forEach(companyName => {
                    const company = companyData[companyName];
                    const charter = results.existingCharters[companyName];
                    html += '<div class="optimization-company-item optimization-company-existing">';
                    html += '<strong>' + getCompanyDisplayName(companyName) + '</strong>';
                    if (charter) {
                        html += ' + Charter: ' + getBuildingDisplayName(charter);
                    }
                    html += '<br><small>Buildings: ' + (company.building_types || []).length;
                    if (charter) html += ' + 1 charter';
                    html += '</small>';
                    html += '</div>';
                });
                html += '</div>';
            }
            
            // Show new recommendations
            if (results.newCompanies.length > 0) {
                html += '<h3>Recommended Additions</h3>';
                html += '<div class="optimization-results">';
                results.newCompanies.forEach(rec => {
                    const company = companyData[rec.name];
                    html += '<div class="optimization-company-item optimization-company-new">';
                    html += '<strong>' + getCompanyDisplayName(rec.name) + '</strong>';
                    if (rec.charter) {
                        html += ' + Charter: ' + getBuildingDisplayName(rec.charter);
                    }
                    html += '<br><small>Adds ' + rec.coverage.length + ' buildings to coverage</small>';
                    html += '</div>';
                });
                html += '</div>';
            }
            
            // Show special recommendations
            if (results.specialRecommendations && results.specialRecommendations.length > 0) {
                html += '<h3>Special Companies (Free Slots)</h3>';
                html += '<div class="optimization-results">';
                results.specialRecommendations.forEach(rec => {
                    html += '<div class="optimization-company-item optimization-company-new">';
                    html += '<strong>' + getCompanyDisplayName(rec.name) + '</strong>';
                    html += '<br><small>Adds coverage without using a company slot</small>';
                    html += '</div>';
                });
                html += '</div>';
            }
            
            // Show uncovered buildings
            if (results.coverage.uncoveredBuildings && results.coverage.uncoveredBuildings.length > 0) {
                html += '<h3>Uncovered Buildings</h3>';
                html += '<div style="color: #666; font-size: 14px;">';
                results.coverage.uncoveredBuildings.forEach(building => {
                    html += getBuildingDisplayName(building) + ', ';
                });
                html = html.slice(0, -2); // Remove trailing comma
                html += '</div>';
            }
            
            resultsEl.innerHTML = html;
        }
        
        function closeOptimizationModal() {
            document.getElementById('optimizationModal').style.display = 'none';
            optimizationResults = null;
        }
        
        function applyOptimizationResults() {
            if (!optimizationResults || !optimizationResults.success) return;
            
            // Clear existing selection if needed
            if (confirm('This will replace your current selection. Continue?')) {
                // Clear all
                localStorage.removeItem(STORAGE_KEY);
                localStorage.removeItem(CHARTER_STORAGE_KEY);
                
                // Add existing companies back
                const newSelection = [...optimizationResults.existingCompanies];
                const newCharters = {...optimizationResults.existingCharters};
                
                // Add new companies
                optimizationResults.newCompanies.forEach(rec => {
                    newSelection.push(rec.name);
                    if (rec.charter) {
                        newCharters[rec.name] = rec.charter;
                    }
                });
                
                // Add special companies
                if (optimizationResults.specialRecommendations) {
                    optimizationResults.specialRecommendations.forEach(rec => {
                        newSelection.push(rec.name);
                    });
                }
                
                // Save
                saveCustomCompanies(newSelection);
                saveSelectedCharters(newCharters);
                
                // Update UI
                updateCustomTable();
                updateCheckboxes();
                updateControlButtons();
                updateDynamicCoverage();
                updateMainBuildingHeaders();
                updateBuildingTableCharters();
                
                // Close modal
                closeOptimizationModal();
            }
        }
        
        function getCompanyDisplayName(companyName) {
            // Convert internal name to display name
            return companyName.replace('company_', '').replace(/_/g, ' ')
                .split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        }
        
        // Function to get building short form (global scope)
        const getBuildingShortForm = (building) => {
            return buildingShortForms[building] || building.replace('building_', '').replace(/_/g, ' ');
        };
        
        window.regenerateSummaryContent = function() {
            console.log('regenerateSummaryContent called');
            // Only update the summary content, not the entire section with checkbox
            const summaryContentDiv = document.getElementById('summary-content');
            const checkbox = document.getElementById('show-prosperity-bonuses');
            
            console.log('summaryContentDiv:', summaryContentDiv);
            console.log('checkbox:', checkbox);
            
            if (!summaryContentDiv) {
                console.error('summary-content div not found');
                return;
            }
            if (!checkbox) {
                console.error('show-prosperity-bonuses checkbox not found');
                return;
            }
            
            const customCompanies = getCustomCompanies();
            const showBonuses = checkbox.checked;
            
            // Regenerate just the company list part
            let summaryContent = '';
            
            customCompanies.forEach(companyName => {
                const company = companyData[companyName];
                if (company) {
                    const companyIconPath = getCompanyIconPath(companyName);
                    const companyDisplayName = company?.name || companyName;
                    
                    summaryContent += `<div style="margin: 2px 0; font-size: 12px; line-height: 1.4;">`;
                    
                    // Company icon and name
                    summaryContent += `<img src="${companyIconPath}" alt="${companyDisplayName}" title="${companyDisplayName}" style="width: 16px; height: 16px; margin-right: 4px; vertical-align: middle;" onerror="this.style.display='none'">`;
                    summaryContent += `<strong>${companyDisplayName}</strong>`;
                    
                    // Add building details (list base buildings, selected charter)
                    const buildingParts = [];
                    
                    // List base buildings by short form
                    if (company.base_buildings && company.base_buildings.length > 0) {
                        const baseNames = company.base_buildings.map(building => getBuildingShortForm(building));
                        buildingParts.push(baseNames.join(', '));
                    }
                    
                    // Add selected charter if any (with + prefix)
                    const selectedCharters = getSelectedCharters();
                    const selectedCharter = selectedCharters[companyName];
                    if (selectedCharter) {
                        const charterName = '+' + getBuildingShortForm(selectedCharter);
                        buildingParts.push(charterName);
                    }
                    
                    if (buildingParts.length > 0) {
                        summaryContent += ` (${buildingParts.join(', ')})`;
                    }
                    
                    // Add prestige goods with icons [formatted like company card]
                    if (company.prestige_goods && company.prestige_goods.length > 0) {
                        summaryContent += ` [`;
                        company.prestige_goods.forEach((prestigeGood, index) => {
                            if (index > 0) summaryContent += ', ';
                            
                            // Get prestige good icon path with proper base name processing
                            const prestigeGoodBase = prestigeGood.replace('prestige_good_generic_', '').replace('prestige_good_', '');
                            
                            // Icon mappings for prestige goods that don't have exact matches
                            const iconMappings = {
                                'burmese_teak': 'teak',
                                'swedish_bar_iron': 'oregrounds_iron'
                            };
                            
                            const mappedBase = iconMappings[prestigeGoodBase] || prestigeGoodBase;
                            const iconPath = `icons/24px-Prestige_${mappedBase}.png`;
                            const fallbackIcon = `icons/40px-Goods_${mappedBase}.png`;
                            
                            summaryContent += `<img src="${iconPath}" alt="${prestigeGood}" title="${prestigeGood}" style="width: 16px; height: 16px; margin: 0 2px; vertical-align: middle;" onerror="this.src='${fallbackIcon}'; this.onerror=null;">`;
                            
                            // Use the same format as in tooltips - just the base name with proper capitalization
                            const prestigeGoodDisplayName = prestigeGood.replace('prestige_good_generic_', '').replace('prestige_good_', '').replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                            
                            summaryContent += prestigeGoodDisplayName;
                        });
                        summaryContent += `]`;
                    }
                    
                    // Add prosperity bonuses if checkbox is checked and company has bonuses
                    if (showBonuses && company.bonuses && company.bonuses.length > 0) {
                        const formattedBonuses = company.bonuses.map(bonus => {
                            return bonus.replace(/_/g, ' ').replace(' add = ', ' +').replace(' mult = ', ' ×');
                        }).join('; ');
                        summaryContent += ` <span style="color: #666; font-style: italic;">(${formattedBonuses})</span>`;
                    }
                    
                    summaryContent += `</div>`;
                }
            });
            
            summaryContentDiv.innerHTML = summaryContent;
        };
        
        window.copyRedditMarkdown = function(event) {
            const summaryContent = document.getElementById('summary-content');
            if (!summaryContent) {
                console.error('No summary content found');
                return;
            }
            
            // Extract text content from the summary, removing HTML and creating reddit-friendly format
            let textContent = '';
            const summaryDivs = summaryContent.querySelectorAll('div');
            
            if (summaryDivs.length === 0) {
                // Fallback: get all text content and add reddit formatting
                const rawText = summaryContent.textContent || summaryContent.innerText || '';
                const lines = rawText.split('\\n');
                lines.forEach(line => {
                    line = line.trim();
                    if (line) {
                        textContent += '    ' + line + '\\n';
                    }
                });
            } else {
                summaryDivs.forEach(div => {
                    // Get text content but remove image alt text and clean it up
                    let lineText = div.textContent || div.innerText || '';
                    lineText = lineText.trim();
                    if (lineText) {
                        // Add 4 spaces before each company line for reddit formatting
                        textContent += '    ' + lineText + '\\n';
                    }
                });
            }
            
            if (!textContent.trim()) {
                console.error('No text content extracted');
                console.error('No content to copy');
                return;
            }
            
            // Add share link at the bottom without "Edit at:" prefix
            const shareURL = generateShareURL(true); // Get URL without showing alert
            if (shareURL) {
                textContent += '\\n' + shareURL;
            }
            
            console.log('Copying text:', textContent); // Debug log
            
            // Copy to clipboard
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(textContent).then(() => {
                    // Show button feedback similar to share button
                    const button = event.target || event.currentTarget;
                    if (button) {
                        const originalText = button.innerHTML;
                        const originalBackground = button.style.background;
                        button.innerHTML = '✓ Copied!';
                        button.style.background = '#28a745';
                        
                        setTimeout(() => {
                            button.innerHTML = originalText;
                            button.style.background = originalBackground;
                        }, 2000);
                    }
                }).catch(err => {
                    console.error('Failed to copy to clipboard:', err);
                    // Remove alert popup - just log the error
                });
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = textContent;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    document.execCommand('copy');
                    const button = event.target;
                    const originalText = button.textContent;
                    button.textContent = '✓ Copied!';
                    button.style.background = '#28a745';
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.style.background = '#007bff';
                    }, 1500);
                } catch (err) {
                    console.error('Fallback copy failed:', err);
                    // Create a more user-friendly fallback
                    const modal = document.createElement('div');
                    modal.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 1px solid #ccc; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); z-index: 10000; max-width: 400px;';
                    modal.innerHTML = `
                        <h4>Copy Build Summary</h4>
                        <textarea readonly style="width: 100%; height: 150px; margin: 10px 0;">${textContent}</textarea>
                        <div style="text-align: right;">
                            <button onclick="this.parentElement.parentElement.remove()" style="padding: 5px 10px; cursor: pointer;">Close</button>
                        </div>
                    `;
                    document.body.appendChild(modal);
                } finally {
                    if (document.body.contains(textArea)) {
                        document.body.removeChild(textArea);
                    }
                }
            }
        };
        
        window.debugShowMissingRequirements = function() {
            const selectedCompanies = getCustomCompanies();
            console.log('Checking formation requirements for', selectedCompanies.length, 'selected companies...');
            
            selectedCompanies.forEach(companyName => {
                const company = companyData[companyName];
                if (company && company.requirements) {
                    company.requirements.forEach(req => {
                        if (req.includes('Control') && !req.includes('(') && !req.includes('Level')) {
                            console.log(`❌ Missing short name for: "${req}" (${company.name})`);
                        }
                    });
                }
            });
        };
        
        // Import/Export functionality
        function exportCompanyPreset() {
            const enabledCompanies = [];
            const companyCheckboxes = document.querySelectorAll('.company-checkbox:checked');
            companyCheckboxes.forEach(checkbox => {
                enabledCompanies.push(checkbox.value);
            });
            
            const preset = {
                name: "Victoria 3 Company Preset",
                timestamp: new Date().toISOString(),
                companies: enabledCompanies
            };
            
            const dataStr = JSON.stringify(preset, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            
            const exportFileDefaultName = `v3co-preset-${new Date().toISOString().slice(0,10)}.json`;
            
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();
        }
        
        function importCompanyPreset(input) {
            const file = input.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const preset = JSON.parse(e.target.result);
                    if (!preset.companies || !Array.isArray(preset.companies)) {
                        alert('Invalid preset file format');
                        return;
                    }
                    
                    // First disable all companies
                    document.querySelectorAll('.company-checkbox').forEach(checkbox => {
                        checkbox.checked = false;
                        updateCompanyVisibility(checkbox);
                    });
                    
                    // Then enable companies from preset
                    preset.companies.forEach(companyId => {
                        const checkbox = document.querySelector(`input[value="${companyId}"]`);
                        if (checkbox) {
                            checkbox.checked = true;
                            updateCompanyVisibility(checkbox);
                        }
                    });
                    
                    // Update all country statuses
                    const countries = new Set();
                    document.querySelectorAll('.company-checkbox').forEach(checkbox => {
                        countries.add(checkbox.dataset.country);
                    });
                    countries.forEach(countryCode => updateCountryStatus(countryCode));
                    
                    alert(`Preset loaded: ${preset.companies.length} companies enabled`);
                    
                } catch (error) {
                    alert('Error loading preset: Invalid JSON file');
                }
            };
            reader.readAsText(file);
            
            // Reset file input
            input.value = '';
        }
    </script>
</body>
</html>'''
        
        all_dynamic_css = column_hiding_css + '\n        /* Dynamic company hiding rules for country filters */\n' + country_hiding_css
        html = html.replace('__COLUMN_HIDING_CSS_PLACEHOLDER__', all_dynamic_css)
        html = html.replace('__YALPS_BUNDLE_PLACEHOLDER__', yalps_bundle)
        return html

    def _get_country_flags_js(self):
        """Generate JavaScript object for country flags"""
        flags_js = []
        for code, flag in self.country_flags.items():
            flags_js.append(f'"{code}": "{flag}"')
        return '{' + ', '.join(flags_js) + '}'
    
    def _get_country_names_js(self):
        """Generate JavaScript object for country names"""
        names_js = []
        country_names = {
            'USA': 'United States', 'GBR': 'Great Britain', 'FRA': 'France', 'DEU': 'Germany',
            'PRU': 'Prussia', 'AUS': 'Austria-Hungary', 'RUS': 'Russia', 'JAP': 'Japan',
            'CHI': 'China', 'ITA': 'Italy', 'SAR': 'Sardinia-Piedmont', 'SPA': 'Spain',
            'TUR': 'Turkey', 'EGY': 'Egypt', 'PER': 'Persia', 'SWE': 'Sweden', 'NOR': 'Norway',
            'DEN': 'Denmark', 'NET': 'Netherlands', 'BEL': 'Belgium', 'SWI': 'Switzerland',
            'BRZ': 'Brazil', 'ARG': 'Argentina', 'CHL': 'Chile', 'COL': 'Colombia', 'MEX': 'Mexico'
        }
        for code, name in country_names.items():
            names_js.append(f'"{code}": "{name}"')
        return '{' + ', '.join(names_js) + '}'
    
    def _get_building_icon_mappings_js(self):
        """Generate JavaScript object for building icon mappings"""
        # Building name mappings for icon files that have different names (from get_building_icon_path)
        building_name_mappings = {
            'building_chemical_plants': 'chemicals_industry',
            'building_textile_mills': 'textile_industry', 
            'building_artillery_foundries': 'artillery_foundry',
            'building_automotive_industry': 'vehicles_industry',
            'building_livestock_ranch': 'cattle_ranch',
            'building_rubber_plantation': 'rubber_lodge',
            'building_vineyard_plantation': 'vineyards'
        }
        
        mappings_js = []
        for building, icon_name in building_name_mappings.items():
            mappings_js.append(f'"{building}": "{icon_name}"')
        return '{' + ', '.join(mappings_js) + '}'
    
    def _get_prestige_icon_mappings_js(self):
        """Generate JavaScript object with prestige icon paths that actually exist"""
        # Special icon mappings for prestige goods that don't have exact icon matches (same as main table logic)
        icon_mappings = {
            'burmese_teak': 'teak',
            'swedish_bar_iron': 'oregrounds_iron'
        }
        
        prestige_icon_paths = {}
        
        # Go through all known prestige goods and find their actual icon paths
        for prestige_good in self.prestige_goods.keys():
            prestige_good_base = prestige_good.replace('prestige_good_generic_', '').replace('prestige_good_', '')
            
            # Apply special mappings
            if prestige_good_base in icon_mappings:
                prestige_good_base = icon_mappings[prestige_good_base]
            
            # Try prestige-specific icon first, fallback to goods icon (same as main table logic)
            prestige_icon_candidates = [
                f"icons/24px-Prestige_{prestige_good_base}.png",
                f"icons/40px-Goods_{prestige_good_base}.png"
            ]
            
            for candidate in prestige_icon_candidates:
                full_path = os.path.join(os.path.dirname(__file__), candidate)
                if os.path.exists(full_path):
                    prestige_icon_paths[prestige_good] = candidate
                    break
            
            # If no icon found, use fallback
            if prestige_good not in prestige_icon_paths:
                prestige_icon_paths[prestige_good] = "icons/40px-Goods_services.png"
        
        # Convert to JavaScript object
        mappings_js = []
        for prestige_good, icon_path in prestige_icon_paths.items():
            mappings_js.append(f'"{prestige_good}": "{icon_path}"')
        return '{' + ', '.join(mappings_js) + '}'
    
    def _get_building_to_goods_js(self):
        """Generate JavaScript object with building to goods mappings"""
        mappings_js = []
        for building, good in self.building_to_goods.items():
            mappings_js.append(f'"{building}": "{good}"')
        return '{' + ', '.join(mappings_js) + '}'
    
    def _get_prestige_to_base_goods_js(self):
        """Generate JavaScript object with prestige good to base good mappings"""
        mappings_js = []
        for prestige_good, base_good in self.prestige_goods.items():
            mappings_js.append(f'"{prestige_good}": "{base_good}"')
        return '{' + ', '.join(mappings_js) + '}'
    
    def _get_company_data_js(self):
        """Generate JavaScript object with company building data"""
        import json
        company_data_js = {}
        for company_name, data in self.companies.items():
            company_data_js[company_name] = {
                'building_types': data.get('building_types', []),
                'extension_building_types': data.get('extension_building_types', [])
            }
        return json.dumps(company_data_js)
    
    def _generate_column_hiding_css(self, buildings):
        """Generate CSS rules to hide table columns for filtered buildings"""
        css_rules = []
        for building in buildings:
            # Create CSS rule to hide both header (th) and data (td) cells for building columns
            # This ensures proper table alignment when columns are filtered
            css_rule = f"        body.hide-building-{building} table th.col-{building}, body.hide-building-{building} table td.col-{building} {{\n            display: none !important;\n        }}\n"
            css_rules.append(css_rule)
        return ''.join(css_rules)
    
    def _generate_country_hiding_css(self, countries_by_continent):
        """Generate CSS rules to hide company rows for filtered countries and individual companies"""
        css_rules = []
        
        # CSS for country-based hiding (legacy)
        for continent_data in countries_by_continent.values():
            for country_info in continent_data['countries']:
                country_code = country_info['code']
                css_rule = f"        body.hide-country-{country_code} tr[data-country=\"{country_code}\"] {{\n            display: none !important;\n        }}\n"
                css_rules.append(css_rule)
        
        # CSS for individual company hiding
        for company_key in self.companies.keys():
            css_rule = f"        body.hide-company-{company_key} tr[data-company=\"{company_key}\"] {{\n            display: none !important;\n        }}\n"
            css_rules.append(css_rule)
        
        return ''.join(css_rules)

    def save_html_report(self, filename="index.html"):
        """Save the HTML report to a file"""
        html_content = self.generate_html_report()
        
        # Apply ID mappings to the HTML template (manual replacement to avoid format issues)
        html_content = html_content.replace('{company_mappings}', self._generate_company_id_mappings())
        html_content = html_content.replace('{building_mappings}', self._generate_building_id_mappings())
        
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