import os
import time
import shutil
import json
import os
import requests
from pathlib import Path


class FileSystem:
    def __init__(self):
        self.current_cwd = Path.cwd()
        self.base_directory = self.current_cwd.parent
        self.biography_directory = Path.joinpath(self.base_directory,"hero-biography")
        self.current_hero_select = ""
        self.hero_bio_folders = [i for i in os.listdir(f"{self.biography_directory}") if not i.startswith("_") and not i.endswith(".md")]

    def __clear_terminal__(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_values(self):
        print(self.current_cwd, self.base_directory, self.biography_directory, self.hero_bio_folders, self.current_hero_select,sep="\n")
        input("...")

    def add_2_spaces(self):
        selected_heroes = []
        hero_name_input_lower = input(f"--------Modify Hero Bio--------\nEnter the name of the hero bio to modify or 'A' for all.\n: ").lower()
        if hero_name_input_lower == "a":
            for i in self.hero_bio_folders:
                selected_heroes.append(i.title())
            #print(selected_heroes)
        elif not hero_name_input_lower in [i.lower() for i in self.hero_bio_folders]:
            print("Hero not found")
            time.sleep(2)
        else:
            selected_heroes.append(hero_name_input_lower.title())
        for hero in selected_heroes:
            hero_bio_path = Path.joinpath(self.biography_directory, f"{hero}", "biography.md")
            if not hero_bio_path.is_file():
                print(f"Biography file [{hero_bio_path}] not found")
                time.sleep(2)
                return
            special_characters = ["!", "#", "*"]
            lines = hero_bio_path.read_text(encoding="utf-8").splitlines(keepends=True)
            for index, text in enumerate(lines):
                if text[0] in special_characters or text == "\n":
                    #print(f"[{index}]|[Special] : {text!r}")
                    continue
                elif text.endswith("  \n"):
                    continue
                else:
                    #print(f"[{index}]|[Text] : {text!r}")
                    lines[index] = text.removesuffix("\n") + "  \n"
                    #print(f"[{index}]|[Text] : {lines[index]!r}")
            hero_bio_path.write_text("".join(lines), encoding="utf-8")

    def create_hero_folder(self):
        hero_name_input_lower = input(f"--------Create Hero Folder---------\nEnter the name of the hero too add.\n: ").lower()
        if hero_name_input_lower in [i.lower() for i in self.hero_bio_folders]:
            print(f"Hero already exists.")
            time.sleep(2)
            return
        
        template_dir = Path.joinpath(self.biography_directory, "_template")
        if not template_dir.exists():
            print(f"Template directory missing.")
            time.sleep(2)
            return
        
        new_hero_dir = Path.joinpath(self.biography_directory, hero_name_input_lower.title())
        shutil.copytree(template_dir, new_hero_dir)
        print(f"Created new hero folder: {new_hero_dir}")
        self.hero_bio_folders.append(hero_name_input_lower.title())

        hero_bio_path = Path.joinpath(new_hero_dir, "biography.md")
        hero_bio_lines = hero_bio_path.read_text(encoding="utf-8").splitlines(keepends=True)
        hero_bio_lines[0] = f"# Biography {hero_name_input_lower.title()}\n"
        hero_bio_path.write_text("".join(hero_bio_lines), encoding="utf-8")
        time.sleep(2)
        self.__clear_terminal__()
        continue_to_links = input(f"{'='*20}\nDo you want to set folder links? [Y/N].\n>").lower()
        if continue_to_links == "y":
            self.current_hero_select = hero_name_input_lower
            self.edit_hero_image_links()
        self.__clear_terminal__()
    
    def edit_hero_image_links(self):
        if self.current_hero_select == "":
            self.current_hero_select = input(f"--------Edit Hero Image Links---------\nEnter the name of the hero folder to edit image links\n: ").lower()
        if self.current_hero_select not in [i.lower() for i in self.hero_bio_folders]:
            print(f"Hero folder does not exist. Returning to main menu")
            self.current_hero_select = ""
            time.sleep(2)
            self.__clear_terminal__()
            return
        
        links_file_path = Path.joinpath(self.biography_directory,self.current_hero_select.title(), "images", "links.json")
        if not links_file_path.is_file():
            print(f"Unable to find links file [{links_file_path}]")
            time.sleep(2)
            return

        file_contents = links_file_path.read_text()
        json_contents:dict = json.loads(file_contents)

        while True:
            print(f"{"="*20}\nImage Links and Values\n{"-"*20}")
            for index, file_name in enumerate(json_contents):
                print(f"{index+1} : {file_name} : '{json_contents[file_name]}'")
            print("-"*20)
            file_links_edit_input = input(f"Select the file index you wish to edit or enter 'X' to exit.\nPress 'N' to add a additional file indexs.\n: ").lower()
            if file_links_edit_input == "x":
                break
            elif file_links_edit_input.lower() == "n":
                json_contents[f"image_part{len(json_contents)+1}"] = ""
                with links_file_path.open("w", encoding="utf-8") as file:
                    json.dump(json_contents, file, indent=4)
                    continue
            try:
                file_index = int(file_links_edit_input)
                if 0 <= file_index < len(json_contents)+1:
                    line_change_text = input("Input text to set to index.\n>")
                    json_contents[f"image_part{file_index}"] = line_change_text
                    with links_file_path.open("w", encoding="utf-8") as file:
                        json.dump(json_contents, file, indent=4)
                else:
                    print("Invalid index selected.")
                    time.sleep(1)
            except ValueError:
                print("Please enter a valid number.")
                time.sleep(1)
        continue_to_download_links = input(f"{'='*20}\nDo you want to DOWNLOAD folder links? [Y/N].\n>").lower()
        if continue_to_download_links == "y":
            self.download_hero_folder_links()
        self.__clear_terminal__()

    def download_hero_folder_links(self):
        if self.current_hero_select == "":
            hero_folder_name = input(f"--------Edit Hero Image Links---------\nEnter the name of the hero folder to download image links\n: ").lower()
        if hero_folder_name not in [i.lower() for i in self.hero_bio_folders]:
            print(f"Hero folder does not exist.")
            time.sleep(2)
            self.__clear_terminal__()
            return
        links_file_path = Path.joinpath(self.biography_directory, hero_folder_name.title(), "images", "links.json")
        if not links_file_path.is_file():
            print(f"Unable to find links file [{links_file_path}]")
            time.sleep(2)
            return
        
        file_contents = links_file_path.read_text()
        json_contents = json.loads(file_contents)

        print(f"{"="*20}\nImage Links and Values\n{"-"*20}")
        for index, file_name in enumerate(json_contents):
            print(f"[{index+1}] : {file_name} : '{json_contents[file_name]}'")
            print("-"*40)
        print("="*20)

        download_options = input(f"Select the file index you wish to download or enter 'A' to try to download All.\n: ").lower()
        download_path = links_file_path.parent

        if download_options == "a":
            for name, url in json_contents.items():
                if url == "":
                    continue
                request_url = requests.get(url)
                if request_url.status_code != 200:
                    print(f"Failed getting image [Status code ({request_url.status_code})]")
                    continue
                response = request_url.headers.get('Content-Type').split("/")[1]
                image_download_path = Path.joinpath(download_path, f"{name}.{response}")
                with open(image_download_path, "wb") as f:
                    f.write(request_url.content)
                print(request_url, response)
    
    def update_markdown_file(self):
        if self.current_hero_select == "":
            hero_folder_name = input(f"Enter the name of the hero folder to update markdown file\n: ").lower()
        if hero_folder_name not in [i.lower() for i in self.hero_bio_folders]:
            print(f"Hero folder does not exist. Returning to main menu")
            time.sleep(2)
            self.__clear_terminal__()
            return
        self.current_hero_select = hero_folder_name.title()
        markdown_file_path = Path.joinpath(self.biography_directory, self.current_hero_select, "biography.md")
        images_file_path = Path.joinpath(self.biography_directory, self.current_hero_select, "images")
        if not markdown_file_path.exists():
            #print(f"Unable to find markdown file [{markdown_file_path}]")
            time.sleep(2)
            return
        dir_images = [image.name for image in Path.iterdir(images_file_path) if image.is_file() and image.name.startswith("image_part")]
        #print(dir_images)
        md_file = markdown_file_path.read_text(encoding="utf-8").splitlines(keepends=True)
        if not md_file:
            md_file = [f"# Biography {self.current_hero_select}\n",]
        elif not "Biography" and not hero_folder_name.title() in md_file[0]:
            #print("bio not")
            md_file[0] = (f"# Biography {hero_folder_name.title()}")
            #print(md_file)
        image_index, chapter_index = 0, 0
        for index, line in enumerate(md_file):
            #print(index, line)
            if line.startswith("!["):
                md_file[index] = f"![image_part{image_index+1}](./images/{dir_images[image_index]})\n"
                image_index += 1
            if line.startswith("## Chapter"):
                md_file[index] = f"## Chapter {chapter_index+1}\n"
                chapter_index += 1
        
        print(image_index, chapter_index, len(dir_images))
        if chapter_index < len(dir_images):
            for i in range(chapter_index, len(dir_images)):
                md_file.append(f"## Chapter {i+1}\n\nTEXT\n\n![image_part{i+1}](./images/{dir_images[i]})\n")
        markdown_write = "\n".join(md_file)
        #print(md_file)
        markdown_file_path.write_text(data=markdown_write, encoding="utf-8")

while True:
    print(f"{'='*20}\nBattleNight Repo Biography tool.\nPick an option below.\n{'-'*30}\n| [X] / exit")
    options = [method for method in dir(FileSystem) if not method.startswith("_") and callable(getattr(FileSystem, method))]
    for i, m in enumerate(options):
        print(f"| [{i}] / {m}")
    print("-"*30)
    main_menu_option = input("> ").lower()
    if main_menu_option == 'x':
        print("Exiting Program...")
        time.sleep(1)
        raise SystemExit()
    else:
        fs = FileSystem()
        func = getattr(fs, options[int(main_menu_option)])
        fs.__clear_terminal__()
        func()