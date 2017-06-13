import os
import re
import csv
import datetime
import mimetypes
import scrapy
import subprocess

from django.shortcuts import render
from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.conf import settings

from .models import *


@login_required(login_url='/admin/login/')
def init_category(request):
    ALL_CATEGORIES = {
        'Shop Electronics': '/cp/electronics/3944',
        'TV & Video': '/cp/televisions-video/1060825',
        'Home Audio & Theater ': '/cp/home-audio-theater/77622',
        'Cell Phones': '/cp/cell-phones/1105910',
        'No-Contract Phones': '/cp/no-contract-phones-plans/1072335',
        'Unlocked Phones': '/cp/5595429',
        'Straight Talk': '/cp/straight-talk-wireless/1045119',
        'Cases & Accessories': '/cp/cell-phone-accessories/133161',
        'Home Automation': '/cp/home-automation/1229875',
        'Wearable Tech': '/cp/wearable-technology/1229723',
        'Computer Software': '/cp/7288037',
        'iPad & Tablets': '/cp/ipad-tablets/1078524',
        'Computers': '/cp/computers/3951',
        'Laptops': '/cp/laptops/1089430',
        'Desktops': '/cp/desktop-computers/132982',
        'Printers & Supplies': '/cp/printers-scanners-copiers/37807',
        'Networking': '/cp/networking/126297',
        'Accessories': '/cp/computer-accessories-peripherals/132959',
        'Auto Electronics': '/cp/car-audio/3947',
        'Video Games': '/cp/video-games/2636',
        'Cameras & Camcorders': '/cp/cameras/133277',
        'Portable Audio': '/cp/ipods-mp3-players/96469',
        'Headphones': '/cp/headphones/1095191',
        'Speakers & Docks': '/cp/1230415',
        'Office': '/cp/office/1229749',
        'Office Supplies': '/cp/office-supplies/1046059',
        'School Supplies ': '/cp/school-supplies/1086045',
        'Office Technology ': '/cp/office-technology/1070964',
        'Cut the Cable': '/cp/cut-the-cable/3682911',
        'Movies & TV': '/cp/movies-tv/4096',
        'Blu-ray Discs': '/cp/blu-ray/616859',
        'Instawatch': '/cp/Instawatch/1228693',
        'Movie DVDs': '/cp/dvds/530598',
        'TV Shows': '/cp/TV-Shows/530719',
        'Video on Demand by VUDU': '/cp/vudu/1084447',
        'Teenage Mutant Ninja Turtles': '/cp/1225660',
        'Music': '/cp/music/4104',
        'Ticketmaster': '/cp/4824813',
        'Musical Instruments': '/cp/musical-instruments/7796869',
        'Books': '/cp/Books/3920',
        'Children`s & Teen Books': '/cp/Childrens-Books/582053',
        'Batman v Superman': '/cp/5570258',
        'Captain America': '/cp/avengers/1229464',
        'Star Wars': '/cp/Star-Wars/1229472',
        'Shop All Home': '/cp/Home/4044',
        'Better Homes and Gardens': '/cp/better-homes-and-garden/1011919',
        'Pioneer Woman': '/cp/the-pioneer-woman/1231327',
        'Bedding': '/cp/Bedding-and-Bedding-Sets/539103',
        'Basic Bedding': '/cp/Basic-Bedding/1095008',
        'Bath': '/cp/bath-accessories/539095',
        'Home Decor': '/cp/Home-Decor/133012',
        'Curtains & Blinds': '/cp/curtains/539105',
        'Lighting': '/cp/home-lighting/133113',
        'Rugs': '/cp/rugs/110892',
        'Furniture': '/cp/furniture/103150',
        'Bedroom': '/cp/bedroom-furniture/102547',
        'Dining Room': '/cp/kitchen-furniture/4037',
        'Kids` Furniture': '/cp/Kids-Furniture/1155958',
        'Living Room': '/cp/living-room-furniture/4038',
        'Office': '/cp/desks-office-furniture/97116',
        'TV Stands': '/cp/tv-stands-entertainment-centers/635499',
        'Mattresses': '/cp/mattresses/539386',
        'Storage & Organization': '/cp/home-storage-organization/90828',
        'Vacuums & Floor Care': '/cp/vacuums-steamers-floor-care/4047',
        'Appliances': '/cp/Home-Appliances/90548',
        'Kitchen & Dining': '/cp/Kitchen-Dining/623679',
        'Cookware, Bakeware & Tools': '/cp/cookware-bakeware/133020',
        'Dining & Entertaining': '/cp/Dining-Entertaining/639999',
        'Kitchen Appliances': '/cp/small-appliances/90546',
        'Kitchen Storage': '/cp/kitchen-storage-organization/1032619',
        'Sewing & Crafts ': '/cp/Arts-Crafts-and-Sewing/1334134',
        'Luggage': '/cp/luggage/444253',
        'Featured Shops': '/cp/Home/4044',
        'Personalized Gifts': '/cp/personalized-gifts/133224',
        'Kids` Rooms': '/cp/Kids-Rooms/1154295',
        'Teen Rooms ': '/cp/Teen-Rooms/1156136',
        'Home Gift Guide': '/cp/home-gift-guide/2144099',
        'Shop All Home Improvement': '/cp/Home-Improvement/1072864',
        'Tools': '/cp/power-tools-hardware/1031899',
        'All Tool Sets': '/cp/1230400',
        'Air Quality': '/cp/air-conditioners-heaters-fans/133032',
        'Heating & Cooling': '/cp/air-conditioners-heaters-fans/133032',
        'Bathroom Renovations': '/cp/bathroom-fixtures-plumbing/1045879',
        'Kitchen Renovations': '/cp/kitchen-renovations/1071485',
        'Light Bulbs': '/cp/Light-Bulbs/1228347',
        'Paint': '/cp/Paint-Home-Decor/1067617',
        'Garage Storage': '/cp/garage-storage/1067618',
        'Patio & Garden': '/cp/patio-garden/5428',
        'Patio Furniture ': '/cp/patio-furniture/91416',
        'Patio & Outdoor Decor ': '/cp/patio-outdoor-decor/1102183',
        'Grills & Outdoor Cooking ': '/cp/Grills-Grilling/4089',
        'Gardening & Lawn': '/cp/gardening-lawncare/4091',
        'Outdoor Power Equipment ': '/cp/outdoor-power-equipment/1102182',
        'Home Safety ': '/cp/home-safety/1068865',
        'Hardware': '/cp/Hardware/1067612',
        'Shop All Clothing': '/cp/clothing/5438',
        'Women`s': '/cp/womens-clothing-apparel/133162',
        'Women`s Plus': '/cp/womens-plus-size-clothing/133195',
        'Juniors': '/cp/Juniors/133201',
        'Maternity': '/cp/maternity-clothes/133284',
        'Intimates & Sleepwear': '/cp/Intimates-Loungewear/1078024',
        'Jewelry': '/cp/jewelry/3891',
        'Wedding & Engagement ': '/cp/engagement-rings-wedding-bands/540912',
        'Watches': '/cp/Watches/3906',
        'Fine Jewelry': '/cp/Fine-Jewelry/1228254',
        'Men`s': '/cp/mens-clothing/133197',
        'Men`s Big & Tall': '/cp/mens-big-and-tall-clothing/133198',
        'Boys': '/cp/boys-clothing/133199',
        'Girls': '/cp/girls-clothing/133202',
        'Baby & Toddlers': '/cp/baby-clothes/584291',
        'School Uniforms': '/cp/School-Uniform-Shop/1086304',
        'Activewear Shop': '/cp/Activewear-for-the-Family/1228424',
        'Swim Shop': '/cp/Swim-Shop/1229269',
        'The Basics Shop': '/cp/1180146',
        'Character Shop': '/cp/character-clothing-shop/1231398',
        'The Cold Weather Shop': '/cp/cold-weather-clothing-shop/639019',
        'Sports Fan Shop': '/cp/Sports-Fan-Shop/1063984',
        'All Shoes': '/cp/Shoes/1045804',
        'Bags & Accessories': '/cp/bags-accessories/1045799',
        'Shop All Baby': '/cp/baby-products/5427',
        'Nursery & Decor': '/cp/414099',
        'Toddler': '/cp/toddler-room/978579',
        'Car Seats': '/cp/baby-car-seats/91365',
        'Strollers': '/cp/baby-strollers/118134',
        'Activities & Gear': '/cp/baby-gear/86323',
        'Feeding': '/cp/baby-feeding/133283',
        'Diapering': '/cp/diapering-potty/486190',
        'Toys': '/cp/baby-toys-toddler-toys/491351',
        'Health & Safety': '/cp/baby-safety/132943',
        'Clothing': '/cp/baby-clothes/584291',
        'Baby Registry': '/cp/Baby-Registry/1229485',
        'Toys': '/cp/toys/4171',
        'Action Figures': '/cp/Action-Figures/4172',
        'Dolls & Dollhouses': '/cp/Dolls-Dollhouses-Stuffed-Toys/4187',
        'Cars, Drones & RC': '/cp/Play-Vehicles-Trains-Remote-Control/1111647',
        'LEGO & Building Sets': '/cp/Building-Sets-Models/4186',
        'Pretend Play': '/cp/Pretend-Play-Arts-Crafts/4173',
        'Electronics for Kids': '/cp/electronics-for-kids/1096069',
        'Learning Toys': '/cp/Learning-Toys/56125',
        'Games & Puzzles': '/cp/games-puzzles/4191',
        'Musical Instruments': '/cp/Musical-Instruments/7796869',
        'Bikes & Ride-Ons': '/cp/bikes-riding-toys/133073',
        'Outdoor Play': '/cp/Outdoor-Play/14521',
        'Boys` Toys': '/cp/Toys-for-Boys/1228478',
        'Girls` Toys': '/cp/Toys-for-Girls/1228477',
        'Video Games': '/cp/video-games/2636',
        'PlayStation 4': '/cp/PS4/1102672',
        'Xbox One': '/cp/Xbox-One/1224908',
        'Nintendo Switch': '/cp/nintendo-switch/4646529',
        'Accessories': '/cp/Accessories/1229019',
        'Digital Gaming': '/cp/4952188',
        'Nintendo 3DS / 2DS': '/cp/Nintendo-3Ds/1086580',
        'Nintendo Wii U / Wii': '/cp/Nintendo-Wii-U-Wii/1098124',
        'PlayStation 3': '/cp/PS3/413799',
        'Shop All Food': '/cp/food/976759',
        'Beverages': '/cp/beverages/976782',
        'Snacks & Cookies': '/cp/snacks/976787',
        'Breakfast & Cereal': '/cp/breakfast-food-cereal/976783',
        'Meals & Pasta': '/cp/grains-pasta/976794',
        'Candy & Gum': '/cp/candy-gum/1096070',
        'Baking': '/cp/baking/976780',
        'Household Essentials': '/cp/household-essentials/1115193',
        'Shop All Pets': '/cp/pet-supplies/5440',
        'Pet Food': '/cp/pet-food/1075304',
        'Dogs': '/cp/dogs/202072',
        'Cats': '/cp/cats/202073',
        'Fish': '/cp/fish/202074',
        'Beauty': '/cp/beauty/1085666',
        'Makeup': '/cp/makeup/1007040',
        'Fragrances': '/cp/fragrances/133225',
        'Skin Care': '/cp/skin-care/1007039',
        'Hair Care': '/cp/hair-care/1007219',
        'Personal Care': '/cp/personal-care/1005862',
        'Shaving': '/cp/shaving/1007220',
        'Oral Care': '/cp/oral-care/1007221',
        'Bath & Body': '/cp/bath-body/1071969',
        'Men`s Grooming': '/cp/mens-grooming/1056884',
        'Health': '/cp/health/976760',
        'Allergy Wellness Center': '/cp/4203616',
        'Home Health Care': '/cp/home-medical-supplies-equipment/1005860',
        'Medicine Cabinet': '/cp/medicine-cabinet/976798',
        'Diabetes Shop ': '/cp/1231757',
        'Health Insurance': '/cp/health-insurance-benefits/1088605',
        'Care Clinic': '/cp/1224932',
        'Vision Center ': '/cp/Walmart-Vision-Centers/1078944',
        'Prescription Eyewear': '/cp/1229596',
        'Shop All Sports': '/cp/sports-and-outdoors/4125',
        'Outdoor Sports': '/cp/outdoor-recreation/546956',
        'Camping': '/cp/camping/4128',
        'Fishing ': '/cp/fishing-gear/111667',
        'Boats & Water Sports': '/cp/Boats-Water-Sports/1208159',
        'Hunting': '/cp/hunting/4155',
        'Recreation': '/cp/1224931',
        'Bikes': '/cp/Bikes/1081404',
        'Game Room': '/cp/Game-Room/4158',
        'Team Sports': '/cp/Team-Sports-Gear/4161',
        'Baseball & Softball': '/cp/Baseball-Gear-Softball-Gear/4162',
        'Sports Fanshop': '/cp/Sports-Fan-Shop/1063984',
        'Exercise & Fitness': '/cp/Sports-Fitness-Equipment/4134',
        'Automotive ': '/cp/Tires/91083',
        'Tires': '/cp/Tires/1077064',
        'Batteries & Accessories': '/cp/Car-Batteries/1104292',
        'Oils & Fluids': '/cp/motor-oil-transmission-fluid-car-lubricant/1104294',
        'Auto Electronics': '/cp/car-audio/3947',
        'Auto Replacement Parts ': '/cp/auto-parts/1074765',
        'Auto Detailing & Car Care ': '/cp/auto-detailing-car-care/1212910',
        'Auto Services ': '/cp/auto-services/1087266',
        'Gift Registry': '/cp/Gifts-Registry/1094765',
        'Baby Registry': '/cp/Baby-Registry/1229485',
        'Wedding Registry': '/cp/Wedding-Registry/1229486',
        '3D Printers': '/cp/3D-Printing/1228636',
        'Gift Cards': '/cp/Gift-Cards/96894',
        'Corporate Gift Card Program': '/cp/Corporate-Gift-Card-Program/1087584',
        'Personalized Gifts': '/cp/133224',
        'Personalized Jewelry ': '/cp/Personalized-Jewelry/532459',
        'Arts, Crafts & Sewing': '/cp/Arts-Crafts-and-Sewing/1334134',
        'Party & Occasions': '/cp/2637',
        'Birthday Shop': '/cp/birthday-shop/8972913',
        'Wedding Shop': '/cp/Wedding-Shop/112776'
    }

    create_category(None, '/', 'All')
    for title, url in ALL_CATEGORIES.items():
        create_category('/', url, title)

    return HttpResponse('Top categories are successfully initiated')


@login_required(login_url='/admin/login/')
def export_products(request):
    if request.method == "POST":
        product_ids = request.POST.get('ids').strip()
        result_csv_fields = request.POST.getlist('props[]')
        path = datetime.datetime.now().strftime("/tmp/.walmart_products_%Y_%m_%d_%H_%M_%S.csv")

        if product_ids == u'':
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.filter(id__in=get_ids(product_ids))

        write_report(queryset, path, result_csv_fields)
        
        wrapper = FileWrapper( open( path, "r" ) )
        content_type = mimetypes.guess_type( path )[0]

        response = HttpResponse(wrapper, content_type = content_type)
        response['Content-Length'] = os.path.getsize( path ) # not FileField instance
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str( os.path.basename( path ) ) # same here        
        return response
    else:
        fields = [f.name for f in Product._meta.get_fields() 
                  if f.name not in ['updated_at', 'is_new']]
        return render(request, 'product_properties.html', locals())    


def write_report(queryset, path, result_csv_fields):
    result = open(path, 'w')
    result_csv = csv.DictWriter(result, fieldnames=result_csv_fields)
    result_csv.writeheader()

    for product in queryset:
        product_ = model_to_dict(product, fields=result_csv_fields)
        for key, val in product_.items():
            if type(val) not in (float, int, long) and val:
                product_[key] = val.encode('utf-8')

        try:
            result_csv.writerow(product_)
        except Exception, e:
            print product_

    result.close()


def get_subcategories(parent='/', title=''):
    """
    return direct child categories
    """
    categories = Category.objects.filter(parent=parent, title__contains=title)
    return [item.url for item in categories]


def create_category(parent, url, title):
    try:
        Category.objects.create(parent_id=parent, url=url, title=title)
    except Exception, e:
        print str(e)


def get_category_products(category, attr='url'):
    """
    param: category as url
    """
    category = Category.objects.get(url=category)
    result = []
    for cate in category.get_all_children():
        for item in Product.objects.filter(category=cate):
            result.append(getattr(item, attr))
    return result


def set_old_category_products(category):
    """
    Set is_new flag False for existing products for the category
    """
    for cate in category.get_all_children():
        Product.objects.filter(category=cate).update(is_new=False)


def get_ids(list_str):
    ids = list_str.replace('\n', ',')
    return [item.strip() for item in ids.split(',') if item.strip()]
