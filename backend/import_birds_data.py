"""
导入中国鸟类名录数据
参考：郑光美《中国鸟类分类与分布名录》第四版
"""
import sys
sys.path.append('.')
from app.db import species_db

# 常见鸟类数据（示例数据集 - 包含 100 种常见鸟类）
CHINESE_BIRDS_DATA = [
    # 鸭形目 - 鸭科
    {"species_cn": "绿头鸭", "species_en": "Mallard", "scientific_name": "Anas platyrhynchos", "order_cn": "雁形目", "family_cn": "鸭科", "common": True},
    {"species_cn": "斑嘴鸭", "species_en": "Eastern Spot-billed Duck", "scientific_name": "Anas zonorhyncha", "order_cn": "雁形目", "family_cn": "鸭科", "common": True},
    {"species_cn": "赤颈鸭", "species_en": "Eurasian Wigeon", "scientific_name": "Mareca penelope", "order_cn": "雁形目", "family_cn": "鸭科", "common": True},
    {"species_cn": "琵嘴鸭", "species_en": "Northern Shoveler", "scientific_name": "Spatula clypeata", "order_cn": "雁形目", "family_cn": "鸭科", "common": True},
    {"species_cn": "绿翅鸭", "species_en": "Eurasian Teal", "scientific_name": "Anas crecca", "order_cn": "雁形目", "family_cn": "鸭科", "common": True},

    # 鸡形目 - 雉科
    {"species_cn": "环颈雉", "species_en": "Common Pheasant", "scientific_name": "Phasianus colchicus", "order_cn": "鸡形目", "family_cn": "雉科", "common": True},
    {"species_cn": "红腹锦鸡", "species_en": "Golden Pheasant", "scientific_name": "Chrysolophus pictus", "order_cn": "鸡形目", "family_cn": "雉科", "common": False, "conservation_level": "国家二级"},
    {"species_cn": "白鹇", "species_en": "Silver Pheasant", "scientific_name": "Lophura nycthemera", "order_cn": "鸡形目", "family_cn": "雉科", "common": False, "conservation_level": "国家二级"},
    {"species_cn": "血雉", "species_en": "Blood Pheasant", "scientific_name": "Ithaginis cruentus", "order_cn": "鸡形目", "family_cn": "雉科", "common": False, "conservation_level": "国家二级"},
    {"species_cn": "勺鸡", "species_en": "Koklass Pheasant", "scientific_name": "Pucrasia macrolopha", "order_cn": "鸡形目", "family_cn": "雉科", "common": False},

    # 鸽形目 - 鸠鸽科
    {"species_cn": "珠颈斑鸠", "species_en": "Spotted Dove", "scientific_name": "Spilopelia chinensis", "order_cn": "鸽形目", "family_cn": "鸠鸽科", "common": True},
    {"species_cn": "山斑鸠", "species_en": "Oriental Turtle Dove", "scientific_name": "Streptopelia orientalis", "order_cn": "鸽形目", "family_cn": "鸠鸽科", "common": True},
    {"species_cn": "灰斑鸠", "species_en": "Eurasian Collared Dove", "scientific_name": "Streptopelia decaocto", "order_cn": "鸽形目", "family_cn": "鸠鸽科", "common": True},
    {"species_cn": "原鸽", "species_en": "Rock Pigeon", "scientific_name": "Columba livia", "order_cn": "鸽形目", "family_cn": "鸠鸽科", "common": True},
    {"species_cn": "岩鸽", "species_en": "Rock Dove", "scientific_name": "Columba rupestris", "order_cn": "鸽形目", "family_cn": "鸠鸽科", "common": True},

    # 佛法僧目 - 翠鸟科
    {"species_cn": "普通翠鸟", "species_en": "Common Kingfisher", "scientific_name": "Alcedo atthis", "order_cn": "佛法僧目", "family_cn": "翠鸟科", "common": True},
    {"species_cn": "蓝翡翠", "species_en": "Black-capped Kingfisher", "scientific_name": "Halcyon pileata", "order_cn": "佛法僧目", "family_cn": "翠鸟科", "common": True},
    {"species_cn": "白胸翡翠", "species_en": "White-throated Kingfisher", "scientific_name": "Halcyon smyrnensis", "order_cn": "佛法僧目", "family_cn": "翠鸟科", "common": True},

    # 犀鸟目 - 戴胜科
    {"species_cn": "戴胜", "species_en": "Eurasian Hoopoe", "scientific_name": "Upupa epops", "order_cn": "犀鸟目", "family_cn": "戴胜科", "common": True},

    # 䴕形目 - 啄木鸟科
    {"species_cn": "大斑啄木鸟", "species_en": "Great Spotted Woodpecker", "scientific_name": "Dendrocopos major", "order_cn": "䴕形目", "family_cn": "啄木鸟科", "common": True},
    {"species_cn": "星头啄木鸟", "species_en": "Grey-headed Woodpecker", "scientific_name": "Picus canus", "order_cn": "䴕形目", "family_cn": "啄木鸟科", "common": True},
    {"species_cn": "绿啄木鸟", "species_en": "European Green Woodpecker", "scientific_name": "Picus viridis", "order_cn": "䴕形目", "family_cn": "啄木鸟科", "common": False},

    # 雀形目 - 百灵科
    {"species_cn": "小云雀", "species_en": "Oriental Skylark", "scientific_name": "Alauda gulgula", "order_cn": "雀形目", "family_cn": "百灵科", "common": True},
    {"species_cn": "云雀", "species_en": "Eurasian Skylark", "scientific_name": "Alauda arvensis", "order_cn": "雀形目", "family_cn": "百灵科", "common": True},

    # 雀形目 - 鹡鸰科
    {"species_cn": "白鹡鸰", "species_en": "White Wagtail", "scientific_name": "Motacilla alba", "order_cn": "雀形目", "family_cn": "鹡鸰科", "common": True},
    {"species_cn": "黄鹡鸰", "species_en": "Citrine Wagtail", "scientific_name": "Motacilla citreola", "order_cn": "雀形目", "family_cn": "鹡鸰科", "common": True},
    {"species_cn": "灰鹡鸰", "species_en": "Grey Wagtail", "scientific_name": "Motacilla cinerea", "order_cn": "雀形目", "family_cn": "鹡鸰科", "common": True},

    # 雀形目 - 山椒鸟科
    {"species_cn": "灰山椒鸟", "species_en": "Ashy Minivet", "scientific_name": "Pericrocotus divaricatus", "order_cn": "雀形目", "family_cn": "山椒鸟科", "common": True},
    {"species_cn": "短嘴山椒鸟", "species_en": "Short-billed Minivet", "scientific_name": "Pericrocotus brevirostris", "order_cn": "雀形目", "family_cn": "山椒鸟科", "common": True},

    # 雀形目 - 鹎科
    {"species_cn": "白头鹎", "species_en": "Light-vented Bulbul", "scientific_name": "Pycnonotus sinensis", "order_cn": "雀形目", "family_cn": "鹎科", "common": True},
    {"species_cn": "红耳鹎", "species_en": "Red-whiskered Bulbul", "scientific_name": "Pycnonotus jocosus", "order_cn": "雀形目", "family_cn": "鹎科", "common": True},
    {"species_cn": "领雀嘴鹎", "species_en": "Collared Finchbill", "scientific_name": "Spizixos semitorques", "order_cn": "雀形目", "family_cn": "鹎科", "common": True},

    # 雀形目 - 伯劳科
    {"species_cn": "红尾伯劳", "species_en": "Brown Shrike", "scientific_name": "Lanius cristatus", "order_cn": "雀形目", "family_cn": "伯劳科", "common": True},
    {"species_cn": "牛头伯劳", "species_en": "Red-backed Shrike", "scientific_name": "Lanius bucephalus", "order_cn": "雀形目", "family_cn": "伯劳科", "common": True},
    {"species_cn": "灰伯劳", "species_en": "Great Grey Shrike", "scientific_name": "Lanius excubitor", "order_cn": "雀形目", "family_cn": "伯劳科", "common": False},

    # 雀形目 - 黄鹂科
    {"species_cn": "黑枕黄鹂", "species_en": "Black-naped Oriole", "scientific_name": "Oriolus chinensis", "order_cn": "雀形目", "family_cn": "黄鹂科", "common": True},

    # 雀形目 - 卷尾科
    {"species_cn": "黑卷尾", "species_en": "Black Drongo", "scientific_name": "Dicrurus macrocercus", "order_cn": "雀形目", "family_cn": "卷尾科", "common": True},
    {"species_cn": "灰卷尾", "species_en": "Ashy Drongo", "scientific_name": "Dicrurus leucophaeus", "order_cn": "雀形目", "family_cn": "卷尾科", "common": True},

    # 雀形目 - 椋鸟科
    {"species_cn": "灰椋鸟", "species_en": "White-cheeked Starling", "scientific_name": "Spodiopsar cineraceus", "order_cn": "雀形目", "family_cn": "椋鸟科", "common": True},
    {"species_cn": "丝光椋鸟", "species_en": "Red-billed Starling", "scientific_name": "Spodiopsar sericeus", "order_cn": "雀形目", "family_cn": "椋鸟科", "common": True},
    {"species_cn": "八哥", "species_en": "Crested Myna", "scientific_name": "Acridotheres cristatellus", "order_cn": "雀形目", "family_cn": "椋鸟科", "common": True},

    # 雀形目 - 鸫科
    {"species_cn": "乌鸫", "species_en": "Common Blackbird", "scientific_name": "Turdus merula", "order_cn": "雀形目", "family_cn": "鸫科", "common": True},
    {"species_cn": "白腹鸫", "species_en": "Pale-throated Thrush", "scientific_name": "Turdus pallidus", "order_cn": "雀形目", "family_cn": "鸫科", "common": True},
    {"species_cn": "斑鸫", "species_en": "Naumann's Thrush", "scientific_name": "Turdus naumanni", "order_cn": "雀形目", "family_cn": "鸫科", "common": True},

    # 雀形目 - 莺科
    {"species_cn": "黄眉柳莺", "species_en": "Yellow-browed Warbler", "scientific_name": "Phylloscopus inornatus", "order_cn": "雀形目", "family_cn": "莺科", "common": True},
    {"species_cn": "双斑绿柳莺", "species_en": "Two-barred Warbler", "scientific_name": "Phylloscopus plumbeitarsus", "order_cn": "雀形目", "family_cn": "莺科", "common": True},
    {"species_cn": "巨嘴柳莺", "species_en": "Radde's Warbler", "scientific_name": "Phylloscopus schwarzi", "order_cn": "雀形目", "family_cn": "莺科", "common": True},

    # 雀形目 - 山雀科
    {"species_cn": "大山雀", "species_en": "Great Tit", "scientific_name": "Parus major", "order_cn": "雀形目", "family_cn": "山雀科", "common": True},
    {"species_cn": "远东山雀", "species_en": "Japanese Tit", "scientific_name": "Parus minor", "order_cn": "雀形目", "family_cn": "山雀科", "common": True},
    {"species_cn": "沼泽山雀", "species_en": "Marsh Tit", "scientific_name": "Poecile palustris", "order_cn": "雀形目", "family_cn": "山雀科", "common": True},
    {"species_cn": "煤山雀", "species_en": "Coal Tit", "scientific_name": "Periparus ater", "order_cn": "雀形目", "family_cn": "山雀科", "common": True},
    {"species_cn": "黄腹山雀", "species_en": "Yellow-bellied Tit", "scientific_name": "Pardaliparus venustulus", "order_cn": "雀形目", "family_cn": "山雀科", "common": True},

    # 雀形目 - 鳾科
    {"species_cn": "普通鳾", "species_en": "Eurasian Nuthatch", "scientific_name": "Sitta europaea", "order_cn": "雀形目", "family_cn": "鳾科", "common": True},
    {"species_cn": "栗臀鳾", "species_en": "Chestnut-vented Nuthatch", "scientific_name": "Sitta nagaensis", "order_cn": "雀形目", "family_cn": "鳾科", "common": True},

    # 雀形目 - 太阳鸟科
    {"species_cn": "叉尾太阳鸟", "species_en": "Mrs. Gould's Sunbird", "scientific_name": "Aethopyga gouldiae", "order_cn": "雀形目", "family_cn": "太阳鸟科", "common": True},
    {"species_cn": "蓝喉太阳鸟", "species_en": "Red-throated Sunbird", "scientific_name": "Aethopyga ignicauda", "order_cn": "雀形目", "family_cn": "太阳鸟科", "common": True},

    # 雀形目 - 绣眼鸟科
    {"species_cn": "暗绿绣眼鸟", "species_en": "Japanese White-eye", "scientific_name": "Zosterops japonicus", "order_cn": "雀形目", "family_cn": "绣眼鸟科", "common": True},
    {"species_cn": "红胁绣眼鸟", "species_en": "Chestnut-flanked White-eye", "scientific_name": "Zosterops erythropleurus", "order_cn": "雀形目", "family_cn": "绣眼鸟科", "common": True},

    # 雀形目 - 雀科
    {"species_cn": "麻雀", "species_en": "Eurasian Tree Sparrow", "scientific_name": "Passer montanus", "order_cn": "雀形目", "family_cn": "雀科", "common": True},
    {"species_cn": "树麻雀", "species_en": "Tree Sparrow", "scientific_name": "Passer montanus", "order_cn": "雀形目", "family_cn": "雀科", "common": True},
    {"species_cn": "金翅雀", "species_en": "Oriental Greenfinch", "scientific_name": "Chloris sinica", "order_cn": "雀形目", "family_cn": "雀科", "common": True},
    {"species_cn": "黄雀", "species_en": "Eurasian Siskin", "scientific_name": "Spinus spinus", "order_cn": "雀形目", "family_cn": "雀科", "common": True},
    {"species_cn": "燕雀", "species_en": "Brambling", "scientific_name": "Fringilla montifringilla", "order_cn": "雀形目", "family_cn": "雀科", "common": True},
    {"species_cn": "黑尾蜡嘴雀", "species_en": "Chinese Hawfinch", "scientific_name": "Eophona migratoria", "order_cn": "雀形目", "family_cn": "雀科", "common": True},
    {"species_cn": "锡嘴雀", "species_en": "Hawfinch", "scientific_name": "Coccothraustes coccothraustes", "order_cn": "雀形目", "family_cn": "雀科", "common": True},

    # 雀形目 - 鹀科
    {"species_cn": "黄胸鹀", "species_en": "Yellow-breasted Bunting", "scientific_name": "Emberiza aureola", "order_cn": "雀形目", "family_cn": "鹀科", "common": True, "conservation_level": "极危"},
    {"species_cn": "三道眉草鹀", "species_en": "Meadow Bunting", "scientific_name": "Emberiza cioides", "order_cn": "雀形目", "family_cn": "鹀科", "common": True},
    {"species_cn": "栗耳鹀", "species_en": "Chestnut-eared Bunting", "scientific_name": "Emberiza fucata", "order_cn": "雀形目", "family_cn": "鹀科", "common": True},
    {"species_cn": "灰头鹀", "species_en": "Grey-headed Bunting", "scientific_name": "Emberiza spodocephala", "order_cn": "雀形目", "family_cn": "鹀科", "common": True},
    {"species_cn": "黄喉鹀", "species_en": "Yellow-throated Bunting", "scientific_name": "Emberiza elegans", "order_cn": "雀形目", "family_cn": "鹀科", "common": True},

    # 隼形目 - 隼科
    {"species_cn": "红隼", "species_en": "Common Kestrel", "scientific_name": "Falco tinnunculus", "order_cn": "隼形目", "family_cn": "隼科", "common": True, "conservation_level": "国家二级"},
    {"species_cn": "燕隼", "species_en": "Eurasian Hobby", "scientific_name": "Falco subbuteo", "order_cn": "隼形目", "family_cn": "隼科", "common": False, "conservation_level": "国家二级"},
    {"species_cn": "游隼", "species_en": "Peregrine Falcon", "scientific_name": "Falco peregrinus", "order_cn": "隼形目", "family_cn": "隼科", "common": False, "conservation_level": "国家二级"},

    # 鹰形目 - 鹰科
    {"species_cn": "黑鸢", "species_en": "Black Kite", "scientific_name": "Milvus migrans", "order_cn": "鹰形目", "family_cn": "鹰科", "common": True, "conservation_level": "国家二级"},
    {"species_cn": "苍鹰", "species_en": "Northern Goshawk", "scientific_name": "Accipiter gentilis", "order_cn": "鹰形目", "family_cn": "鹰科", "common": False, "conservation_level": "国家二级"},
    {"species_cn": "松雀鹰", "species_en": "Besra", "scientific_name": "Accipiter virgatus", "order_cn": "鹰形目", "family_cn": "鹰科", "common": False, "conservation_level": "国家二级"},
    {"species_cn": "普通鵟", "species_en": "Common Buzzard", "scientific_name": "Buteo buteo", "order_cn": "鹰形目", "family_cn": "鹰科", "common": True, "conservation_level": "国家二级"},

    # 鸮形目 - 鸱鸮科
    {"species_cn": "领角鸮", "species_en": "Collared Scops Owl", "scientific_name": "Otus lettia", "order_cn": "鸮形目", "family_cn": "鸱鸮科", "common": False, "conservation_level": "国家二级"},
    {"species_cn": "红角鸮", "species_en": "Oriental Scops Owl", "scientific_name": "Otus sunia", "order_cn": "鸮形目", "family_cn": "鸱鸮科", "common": False, "conservation_level": "国家二级"},
    {"species_cn": "长耳鸮", "species_en": "Long-eared Owl", "scientific_name": "Asio otus", "order_cn": "鸮形目", "family_cn": "鸱鸮科", "common": False, "conservation_level": "国家二级"},
    {"species_cn": "短耳鸮", "species_en": "Short-eared Owl", "scientific_name": "Asio flammeus", "order_cn": "鸮形目", "family_cn": "鸱鸮科", "common": False, "conservation_level": "国家二级"},

    # 鹤形目 - 秧鸡科
    {"species_cn": "黑水鸡", "species_en": "Common Moorhen", "scientific_name": "Gallinula chloropus", "order_cn": "鹤形目", "family_cn": "秧鸡科", "common": True},
    {"species_cn": "白骨顶", "species_en": "Eurasian Coot", "scientific_name": "Fulica atra", "order_cn": "鹤形目", "family_cn": "秧鸡科", "common": True},
    {"species_cn": "小田鸡", "species_en": "Little Crake", "scientific_name": "Zapornia parva", "order_cn": "鹤形目", "family_cn": "秧鸡科", "common": False},

    # 鸻形目 - 鸻科
    {"species_cn": "金眶鸻", "species_en": "Little Ringed Plover", "scientific_name": "Charadrius dubius", "order_cn": "鸻形目", "family_cn": "鸻科", "common": True},
    {"species_cn": "长嘴剑鸻", "species_en": "Long-billed Plover", "scientific_name": "Charadrius placidus", "order_cn": "鸻形目", "family_cn": "鸻科", "common": True},

    # 鸻形目 - 鹬科
    {"species_cn": "矶鹬", "species_en": "Common Sandpiper", "scientific_name": "Actitis hypoleucos", "order_cn": "鸻形目", "family_cn": "鹬科", "common": True},
    {"species_cn": "林鹬", "species_en": "Common Greenshank", "scientific_name": "Tringa nebularia", "order_cn": "鸻形目", "family_cn": "鹬科", "common": True},
    {"species_cn": "红脚鹬", "species_en": "Common Redshank", "scientific_name": "Tringa totanus", "order_cn": "鸻形目", "family_cn": "鹬科", "common": True},

    # 鹈形目 - 鹭科
    {"species_cn": "苍鹭", "species_en": "Grey Heron", "scientific_name": "Ardea cinerea", "order_cn": "鹈形目", "family_cn": "鹭科", "common": True},
    {"species_cn": "草鹭", "species_en": "Purple Heron", "scientific_name": "Ardea purpurea", "order_cn": "鹈形目", "family_cn": "鹭科", "common": True},
    {"species_cn": "大白鹭", "species_en": "Great Egret", "scientific_name": "Ardea alba", "order_cn": "鹈形目", "family_cn": "鹭科", "common": True},
    {"species_cn": "中白鹭", "species_en": "Intermediate Egret", "scientific_name": "Ardea intermedia", "order_cn": "鹈形目", "family_cn": "鹭科", "common": True},
    {"species_cn": "白鹭", "species_en": "Little Egret", "scientific_name": "Egretta garzetta", "order_cn": "鹈形目", "family_cn": "鹭科", "common": True},
    {"species_cn": "夜鹭", "species_en": "Black-crowned Night Heron", "scientific_name": "Nycticorax nycticorax", "order_cn": "鹈形目", "family_cn": "鹭科", "common": True},
    {"species_cn": "池鹭", "species_en": "Chinese Pond Heron", "scientific_name": "Ardeola bacchus", "order_cn": "鹈形目", "family_cn": "鹭科", "common": True},
    {"species_cn": "牛背鹭", "species_en": "Cattle Egret", "scientific_name": "Bubulcus ibis", "order_cn": "鹈形目", "family_cn": "鹭科", "common": True},
    {"species_cn": "黄斑苇鳽", "species_en": "Yellow Bittern", "scientific_name": "Ixobrychus sinensis", "order_cn": "鹈形目", "family_cn": "鹭科", "common": True},

    # 雨燕目 - 雨燕科
    {"species_cn": "北京雨燕", "species_en": "Beijing Swift", "scientific_name": "Apus apus pekinensis", "order_cn": "雨燕目", "family_cn": "雨燕科", "common": True},
    {"species_cn": "白腰雨燕", "species_en": "Pacific Swift", "scientific_name": "Apus pacificus", "order_cn": "雨燕目", "family_cn": "雨燕科", "common": True},

    # 佛法僧目 - 夜鹰科
    {"species_cn": "普通夜鹰", "species_en": "European Nightjar", "scientific_name": "Caprimulgus europaeus", "order_cn": "夜鹰目", "family_cn": "夜鹰科", "common": False},
]


def import_data():
    """导入鸟类数据"""
    count = species_db.batch_add_species(CHINESE_BIRDS_DATA)
    print(f"成功导入 {count} 种鸟类")
    return count


if __name__ == "__main__":
    import_data()
