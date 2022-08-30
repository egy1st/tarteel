from constants import are_we_live, PAGE_CONFIG

def get_images_parent_path(resolution="1024"):
    path = '/static/ayat/N1/img/T2/02'
    return path

def get_image_path_from_safah(safah=1, images='1024'):
    page_file_name = PAGE_CONFIG[images]['format'].format(safah)  
    images_parent_path = get_images_parent_path(images)
    page_path = images_parent_path + '/' + page_file_name 
    #page_path = page_file_name  # maa
    return page_path