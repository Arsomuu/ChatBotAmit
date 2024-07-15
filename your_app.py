import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.metrics import dp

from PIL import Image as PILImage, ImageDraw, ImageFont

class ChatBotApp(App):
    def build(self):
        self.university_info = read_resource_file('university_info.txt')
        self.user_icon_path = None
        self.bot_icon_path = 'bot_icon.png'  # Use the bot icon image file

        self.root = FloatLayout()
        self.show_landing_page()
        return self.root

    def show_landing_page(self):
        layout = FloatLayout()

        label = Label(
            text="Enter your name:",
            size_hint=(.6, .1),
            pos_hint={'x': .2, 'y': .5},
            font_size='18sp'
        )
        self.name_entry = TextInput(
            size_hint=(.6, .1),
            pos_hint={'x': .2, 'y': .4},
            multiline=False
        )
        self.name_entry.bind(on_text_validate=self.start_chat)
        self.name_entry.focus = True  # Set focus on the name input field
        
        start_button = Button(
            text="Start Chat",
            size_hint=(.6, .1),
            pos_hint={'x': .2, 'y': .3},
            on_press=self.start_chat
        )

        layout.add_widget(label)
        layout.add_widget(self.name_entry)
        layout.add_widget(start_button)

        self.root.add_widget(layout)

    def create_chat_ui(self):
        layout = BoxLayout(orientation='vertical')

        self.heading_label = Label(
            text="University Help Desk",
            size_hint=(1, None),
            height=dp(50),
            font_size='24sp',
            bold=True
        )
        layout.add_widget(self.heading_label)

        self.chat_display = ScrollView()
        self.chat_history = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(10)
        )
        self.chat_history.bind(minimum_height=self.chat_history.setter('height'))
        self.chat_display.add_widget(self.chat_history)
        layout.add_widget(self.chat_display)

        input_layout = BoxLayout(size_hint=(1, None), height=dp(60))
        self.query_entry = TextInput(
            size_hint_x=0.8,
            multiline=False
        )
        self.query_entry.bind(on_text_validate=self.send_query)
        send_button = Button(
            text="Send",
            size_hint_x=0.2,
            background_color=(0.2, 0.6, 1, 1),
            on_press=self.send_query
        )
        input_layout.add_widget(self.query_entry)
        input_layout.add_widget(send_button)

        layout.add_widget(input_layout)

        return layout

    def start_chat(self, instance):
        user_name = self.name_entry.text
        if user_name:
            self.user_icon_path = create_circle_image(user_name[0].upper())
            self.root.clear_widgets()
            self.root.add_widget(self.create_chat_ui())
            self.display_initial_message()
            Clock.schedule_once(lambda dt: setattr(self.query_entry, 'focus', True), 0.1)
        else:
            self.show_popup('Error', 'Please enter a name.')

    def send_query(self, instance):
        query = self.query_entry.text
        if query.lower() in ['exit', 'quit', 'bye']:
            App.get_running_app().stop()
            return
        elif query.lower() == 'clear':
            self.chat_history.clear_widgets()
            self.query_entry.text = ''
            Clock.schedule_once(lambda dt: setattr(self.query_entry, 'focus', True), 0.1)
            return
        self.query_entry.text = ''
        self.display_message("You", query, icon=self.user_icon_path)
        response = self.respond(query)
        self.display_message("Chatbot", response, icon=self.bot_icon_path)
        Clock.schedule_once(lambda dt: setattr(self.query_entry, 'focus', True), 0.1)

    def respond(self, query):
        query = query.lower()
        for key, value in self.university_info.items():
            if key in query:
                return f"{key.capitalize()}: {value}"
        return "I'm sorry, I don't have information on that topic."

    def display_initial_message(self):
        self.display_message("Chatbot", "How can I help you?", icon=self.bot_icon_path)

    def display_message(self, sender, message, icon):
        message_layout = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10), spacing=dp(10))

        if sender == "You":
            message_layout.size_hint_x = None
            message_layout.width = dp(300)  # Fixed width for user messages
            message_layout.pos_hint = {'right': 1.0}
            message_layout.background_color = (0.8, 0.8, 0.8, 1)  # Light gray for user messages
            align = 'right'
        else:
            message_layout.size_hint_x = None
            message_layout.width = dp(300)  # Fixed width for bot messages
            message_layout.pos_hint = {'left': 1.0}
            message_layout.background_color = (0.8, 0.8, 0.8, 1)  # Light gray for bot messages
            align = 'left'

        if icon:
            img = Image(source=icon, size_hint=(None, None), size=(dp(40), dp(40)))
            message_layout.add_widget(img)

        # Ensure enough space for the text
        bubble = BoxLayout(orientation='vertical', size_hint_x=1)
        bubble_layout = BoxLayout(size_hint=(1, None), width=dp(230))
        message_label = Label(text=message, valign='middle', halign=align, text_size=(dp(230), None))
        message_label.bind(size=message_label.setter('text_size'))  # Ensure text is wrapped correctly
        bubble_layout.add_widget(message_label)
        bubble.add_widget(bubble_layout)

        message_layout.add_widget(bubble)
        self.chat_history.add_widget(message_layout)
        self.chat_display.scroll_y = 0

        Clock.schedule_once(lambda dt: setattr(self.query_entry, 'focus', True), 0.1)

    def show_popup(self, title, message):
        layout = FloatLayout()
        popup_label = Label(
            text=message,
            size_hint=(.8, .2),
            pos_hint={'x': .1, 'y': .5},
            font_size='18sp'
        )
        close_button = Button(
            text="Close",
            size_hint=(.2, .1),
            pos_hint={'x': .4, 'y': .3},
            on_press=self.close_popup
        )
        layout.add_widget(popup_label)
        layout.add_widget(close_button)

        self.popup = Popup(title=title, content=layout, size_hint=(0.8, 0.5))
        self.popup.open()

    def close_popup(self, instance):
        self.popup.dismiss()

def read_resource_file(filename):
    university_info = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split(': ')
            university_info[key.lower()] = value
    return university_info

def create_circle_image(text, size=50, font_size=20):
    image = PILImage.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, size, size), fill='blue')

    font = ImageFont.truetype("arial.ttf", font_size)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    text_x = (size - text_width) / 2
    text_y = (size - text_height) / 2
    draw.text((text_x, text_y), text, font=font, fill='white')

    image_path = f'{text}_icon.png'
    image.save(image_path)
    return image_path

if __name__ == "__main__":
    ChatBotApp().run()