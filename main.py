import os
import io
import ctypes
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from tkinter.font import nametofont, Font

ctypes.windll.shcore.SetProcessDpiAwareness(1)

comp_details = {
    "DC Voltage Source": ["Positive", "Negative"],
    "DC V. Source (One Terminal)": ["DC V. Source (One Terminal)"],
    "AC Voltage Source": ["AC Voltage Source"],
    "DC Current Source": ["Flowing From","Flowing To"] ,
    "AC Current Source": ["AC Current Source"],
    "Ground": ["Ground"],
    "Wire Overlap": ["Curved-wire", "Straight-wire"],
    "Resistor": ["Resistor"],
    "Capacitor": ["Capacitor"],
    "Inductor": ["Inductor"],
    "Diode": ["Anode", "Cathode"],
    "Zener diode": ["Anode", "Cathode"],
    "BJT (NPN)": ["Collector", "Base", "Emitter"],
    "BJT (PNP)": ["Emitter", "Base", "Collector"],
    "MOSFET (N-Channel)": ["Drain", "Gate", "Source"],
    "MOSFET (P-Channel)": ["Source", "Gate", "Drain"],
    "Op-Amp": ["In+", "In-", "Out"]
}



# List of terminal of selcted component
selected_comp =""
comp_terminals = ["Select a component first!"]
no_of_terminals = len(comp_terminals)

# Initialize lists to hold image buffers, probability images, and coordinates for each canvas
image_buffers = []
probability_images = []
coords_lists = []
overlay_images =[]

# Loop to initialize each canvas
for i in range(no_of_terminals):
    # Create an image buffer for the canvas
    buffer = Image.new('RGB', (640, 640), 'black')
    image_buffers.append(buffer)
    overlay_images.append(buffer)

    # Create a probability image for the canvas
    probability_image = np.zeros((640, 640), dtype=np.float32)
    probability_images.append(probability_image)

    # Create an empty list of coordinates for the canvas
    coords_list = []
    coords_lists.append(coords_list)


def comp_selected(event):
    global canvases_in
    global selected_comp
    global comp_terminals
    global no_of_terminals
    global notebooks_out
    global canvas_out_lists
    global image_buffers
    global probability_images
    global coords_lists
    global overlay_images

    selected_comp = comp_select.get()
    comp_terminals = comp_details[selected_comp]
    no_of_terminals = len(comp_terminals)

    for canvas in canvases_in:
        canvas.destroy()

    canvases_in = []

    # Create canvases, add to notebook, bind event, and store references
    for text in comp_terminals:
        canvas = tk.Canvas(root, width=640, height=640, bg='gray80', relief='sunken', cursor='crosshair', bd=0, highlightthickness=0)
        notebook_input.add(canvas, text=f'  {text}  ')
        canvas.bind("<Button-1>", on_canvas_click)
        canvases_in.append(canvas)



    # Defining output notebooks and canvases

    # Hide all notebooks
    for notebook in notebooks_out:
        notebook.destroy()

    for canvases in canvas_out_lists:
        for canvas in canvases:
            canvas.destroy()

    # List to store notebook references
    notebooks_out = []

    # List to store canvas lists for each notebook
    canvas_out_lists = []

    # Names and backgrounds for each type of canvas
    canvas_types = [
        ('Gaussian Heatmap', 'gray80'),
        ('Heatmap Overlay', 'gray80'),
        ('Grayscale Output', 'black')
    ]

    # Create notebooks and canvases
    for i in range(no_of_terminals):
        # Create a notebook widget
        notebook = ttk.Notebook(root)
        notebook.place(x=720, y=152)  # Adjust placement for illustration; might need adjustment

        # List to hold canvases for this notebook
        canvases_out = []

        # Create canvases for each type
        for name, bg in canvas_types:
            canvas = tk.Canvas(root, width=640, height=640, bg=bg, relief='sunken', bd=0, highlightthickness=0)
            notebook.add(canvas, text=f' {name} ')
            canvases_out.append(canvas)

        # Select the 'Heatmap Overlay' by default
        notebook.select(canvases_out[1])

        # Store the notebook and canvas list
        notebooks_out.append(notebook)
        canvas_out_lists.append(canvases_out)

    image_buffers = []
    probability_images = []
    coords_lists = []
    overlay_images =[]


    # Loop to initialize each canvas
    for i in range(no_of_terminals):
        # Create an image buffer for the canvas
        buffer = Image.new('RGB', (640, 640), 'black')
        image_buffers.append(buffer)
        overlay_images.append(buffer)

        # Create a probability image for the canvas
        probability_image = np.zeros((640, 640), dtype=np.float32)
        probability_images.append(probability_image)

        # Create an empty list of coordinates for the canvas
        coords_list = []
        coords_lists.append(coords_list)

    show_image()



def on_tab_selected(event):
    # Get the index of the currently selected tab
    selected_tab = notebook_input.index(notebook_input.select())

    # Hide all notebooks
    for notebook in notebooks_out:
        notebook.place_forget()

    notebooks_out[selected_tab].place(x=720, y=152)




def input_dir():
    directory = askdirectory()
    if directory:
        input_directory.config(text=directory)
        global image_files
        image_files = [os.path.join(directory, f) for f in os.listdir(directory) if
                       f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        global current_image
        current_image = 0
        show_image()
        open_images.config(text="")


def save_dir():
    directory = askdirectory()
    if directory:
        save_directory.config(text=directory)

def clear_canvases():
    for canvases in canvas_out_lists:
        for canvas in canvases:
            canvas.delete('all')



def open_imgs():
    global image_files
    filetypes = [("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
    image_files = filedialog.askopenfilenames(title="Open images", initialdir="/", filetypes=filetypes)
    open_images.config(text=f"Total images selected: {len(image_files)}")
    global current_image
    current_image = 0
    show_image()
    clear_canvases()
    saved_as.config(text="")
    input_directory.config(text="")



def show_prev_image():
    global current_image
    if image_files and current_image > 0:
        current_image -= 1
        show_image()
        clear_canvases()
        saved_as.config(text="")
        notebook_input.select(canvases_in[0])

def show_next_image():
    global current_image
    if image_files and current_image < len(image_files) - 1:
        current_image += 1
        show_image()
        clear_canvases()
        saved_as.config(text="")
        notebook_input.select(canvases_in[0])

def undo():
    selected_tab = notebook_input.index(notebook_input.select())

    # Reset probability image and coordinates for this tab
    probability_images[selected_tab] = np.zeros((640, 640), dtype=np.float32)
    coords_lists[selected_tab] = []

    # Load the image and update the buffer for the current image
    image_path = image_files[current_image]  # Ensure image_files and current_image are defined and accessible
    image_buffers[selected_tab] = Image.open(image_path)

    # Update the canvas with the new image
    image = ImageTk.PhotoImage(image_buffers[selected_tab])
    canvases_in[selected_tab].image = image  # Keep a reference to prevent garbage collection
    canvases_in[selected_tab].create_image(0, 0, image=image, anchor="nw")

    for i in range(len(canvas_out_lists[selected_tab])):
        canvas_out_lists[selected_tab][i].delete("all")

    saved_as.config(text="")


def show_image():

    if image_files:

        for i in range(no_of_terminals):  # Loop from 1 to 3

            # Initialize or clear the variables for this iteration

            probability_images[i] = np.zeros((640, 640), dtype=np.float32)
            coords_lists[i] = []

            image_path = image_files[current_image]
            image_buffers[i] = Image.open(image_path)

            # Create and display the image on a canvas
            image = ImageTk.PhotoImage(image_buffers[i])
            canvases_in[i].image = image  # Assumes that 'canvas_1' is a global variable and accessible
            canvases_in[i].create_image(0, 0, image=image, anchor="nw")

        # Update the image name displayed in the UI
        image_name = os.path.basename(image_path)  # Extract the image name
        img_name.config(text=image_name)  # Assumes 'img_name' is a global and accessible

        notebook_input.select(canvases_in[0])



def gaussian_heatmap(shape, center, sigma=1):
    """
    Generate a Gaussian heatmap centered at the specified coordinate.

    Args:
    - shape: Shape of the heatmap.
    - center: Coordinate (x, y) around which the heatmap is centered.
    - sigma: Standard deviation of the Gaussian distribution.

    Returns:
    - Heatmap with Gaussian intensity values.
    """
    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    x_center, y_center = center
    dist = np.sqrt((x - x_center) ** 2 + (y - y_center) ** 2)

    intensity = np.exp(-dist ** 2 / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))
    return intensity


def on_canvas_click(event):

    global overlay_images

    saved_as.config(text="")

    try:
        # Get the index of the clicked canvas
        canvas_index = canvases_in.index(event.widget)
    except ValueError:
        # This error occurs if event.widget is not in canvases
        print("Clicked widget is not a recognized canvas.")
        return


    #print(f"Cursor position at click: ({event.x}, {event.y})")


    # Draw a crosshair at the click position
    draw = ImageDraw.Draw(image_buffers[canvas_index])
    x, y = event.x, event.y

    coords_lists[canvas_index].append(x)
    coords_lists[canvas_index].append(y)

    # Drawing the crosshair with a border
    border_size = 1  # The thickness of the border
    crosshair_size = 8  # The size of the crosshair
    line_width = 2  # The thickness of the crosshair lines
    border_color = 'black'  # Color of the border
    crosshair_color = 'gold'  # Color of the crosshair

    # Draw the border lines (bigger and in the border color)
    draw.line((x - crosshair_size - border_size, y, x + crosshair_size + border_size, y), fill=border_color,
              width=line_width + (border_size * 2))
    draw.line((x, y - crosshair_size - border_size, x, y + crosshair_size + border_size), fill=border_color,
              width=line_width + (border_size * 2))

    # Draw the crosshair lines on top of the border lines (in the crosshair color)
    draw.line((x - crosshair_size, y, x + crosshair_size, y), fill=crosshair_color, width=line_width)
    draw.line((x, y - crosshair_size, x, y + crosshair_size), fill=crosshair_color, width=line_width)

    # Update the canvas image
    image_crosshair = ImageTk.PhotoImage(image_buffers[canvas_index])
    canvases_in[canvas_index].image = image_crosshair
    canvases_in[canvas_index].create_image(0, 0, image=image_crosshair, anchor="nw")

    # Grayscale output image

    heatmap = gaussian_heatmap((640, 640), [event.x, event.y], sigma=25)  # Adjust sigma for desired spread
    probability_images[canvas_index] = np.maximum(probability_images[canvas_index], heatmap)

    probability_image = probability_images[canvas_index].copy()

    # Normalize the probability image
    probability_image /= np.max(probability_image)
    probability_image = (probability_image * 255).astype(np.uint8)

    # Convert the NumPy array to a PIL Image
    probability_image_pil = Image.fromarray(probability_image)

    # Convert the PIL Image to a Tkinter PhotoImage
    probability_image_tk = ImageTk.PhotoImage(probability_image_pil)

    canvas_out_lists[canvas_index][2].image = probability_image_tk
    canvas_out_lists[canvas_index][2].create_image(0, 0, image=probability_image_tk, anchor="nw")

    # Gaussian Heatmap matplotlib

    fig = Figure(figsize=(6.4, 6.4), dpi=100)
    plot = fig.add_subplot(1, 1, 1)
    cax = plot.imshow(probability_image, cmap='jet')
    plot.set_title('Generated Gaussian Heatmap', pad=15)
    fig.colorbar(cax, ax=plot, fraction=0.046, pad=0.04)  # Adjust fraction and pad to fit
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')  # Save the figure to the in-memory file
    buf.seek(0)  # Rewind the file object to its beginning
    buf = io.BytesIO()
    fig.savefig(buf, format='png')  # Save the figure to the in-memory file
    buf.seek(0)  # Rewind the file object to its beginning

    heatmap_image_tk = ImageTk.PhotoImage(data=buf.read())
    canvas_out_lists[canvas_index][0].create_image(0, 0, anchor="nw", image=heatmap_image_tk)  # Adjust anchor and position as needed
    canvas_out_lists[canvas_index][0].image = heatmap_image_tk  # Important: Keep a reference to the image object to prevent it from being garbage collected
    buf.close()

    # Overlay Image

    normalized_heatmap = probability_image.astype(np.float32) / np.max(probability_image)

    colormap = plt.colormaps['jet']  # Map the normalized heatmap to a colormap (RGBA) - using the 'jet' colormap here
    heatmap_rgba = colormap(normalized_heatmap)  # This gives us a normalized [0,1] RGBA image

    heatmap_rgba = np.uint8(heatmap_rgba * 255)  # Convert the RGBA image from [0,1] to [0,255] and to uint8
    heatmap_image = Image.fromarray(heatmap_rgba, 'RGBA')  # Convert to a PIL image

    base_image = image_buffers[canvas_index].convert('RGBA')
    overlay_image = Image.blend(base_image, heatmap_image,
                                alpha=0.5)  # Overlay the heatmap RGBA image onto the base image
    overlay_images[canvas_index] = overlay_image
    overlay_image_tk = ImageTk.PhotoImage(overlay_image)
    canvas_out_lists[canvas_index][1].image = overlay_image_tk
    canvas_out_lists[canvas_index][1].create_image(0, 0, image=overlay_image_tk, anchor="nw")




def save():

    if save_directory.cget("text"):
        if comp_terminals == ["Select a component first!"]:

            saved_as.config(text="Select a component first!")

        else:
            for i in range(no_of_terminals):

                probability_image = probability_images[i]

                # Normalize the probability image
                if np.max(probability_image) == 0:
                    saved_as.config(text="Missing labels for one or more terminals!")
                    return
                else:
                    probability_image /= np.max(probability_image)

                probability_image = (probability_image * 255).astype(np.uint8)

                probability_image_pil = Image.fromarray(probability_image)

                save_dir = os.path.join(save_directory.cget("text"), selected_comp)

                output_dir = os.path.join(save_dir, "Output Maps")

                if no_of_terminals == 1:
                    images_dir = output_dir
                else:
                    images_dir = os.path.join(output_dir, f"{comp_terminals[i]}")

                if not os.path.exists(images_dir):
                    os.makedirs(images_dir)

                image_path = image_files[current_image]
                image_name = os.path.basename(image_path)

                name_without_extension, extension = os.path.splitext(image_name)
                modified_image_name = f"{name_without_extension}_{comp_terminals[i]}{extension}".lower()
                modified_image_name_overlay = f"{name_without_extension}_{comp_terminals[i]}_heatmap{extension}".lower()

                probability_image_path = os.path.join(images_dir, modified_image_name)
                overlay_image_path = os.path.join(images_dir, modified_image_name_overlay)
                probability_image_pil.save(probability_image_path)
                overlay_images[i].save(overlay_image_path)

                if i==0:
                    input_img = Image.open(image_path)
                    input_image_dir = os.path.join(save_dir, "Input Images")
                    if not os.path.exists(input_image_dir):
                        os.makedirs(input_image_dir)
                    input_img.save(os.path.join(input_image_dir, image_name))


                # Saving coordinates txt file

                coords_dir = os.path.join(save_dir, "XY Coordinates")

                if not os.path.exists(coords_dir):
                    os.makedirs(coords_dir)

                txtfile_name = f"{name_without_extension}.txt"
                txtfile_path = os.path.join(coords_dir, txtfile_name)

                # Convert all elements in coords to strings and join them with a space
                final_string = ' '.join(map(str, coords_lists[i]))

                if no_of_terminals == 1:
                        with open(txtfile_path, 'w') as file:
                            file.write(f"{final_string}\n")
                else:
                    if i==0:
                        with open(txtfile_path, 'w') as file:
                            file.write(f"{comp_terminals[i]} {final_string}\n")
                    else:
                        with open(txtfile_path, 'a') as file:
                            file.write(f"{comp_terminals[i]} {final_string}\n")

            saved_as.config(text="Saved successfully!")


    else:
        saved_as.config(text="Select a directory to save first!")







# Initialize the global variables

image_files = []
current_image = 0

root = tk.Tk()
root.title('Gaussian Heatmap Generator')
root.geometry("1395x890+5+5")

style = ttk.Style(root)
style.configure('lefttab.TNotebook', tabposition='ne')


# Get the default font
default_font = nametofont("TkDefaultFont")
italic_font_config = default_font.actual()
italic_font_config["slant"] = "italic"
italic_font = nametofont("TkDefaultFont").copy()
italic_font.config(**italic_font_config)


larger_font = Font(family=default_font.actual("family"), size=default_font.actual("size") + 5)
large_font = Font(family=default_font.actual("family"), size=default_font.actual("size") + 3)

open_imgs_btn = ttk.Button(root, text="Open Images", command=open_imgs)
input_dir_btn = ttk.Button(root, text="Input Directory", command=input_dir)
save_dir_btn = ttk.Button(root, text="Saving Directory", command=save_dir)

open_images = ttk.Label(root,
                        text="",
                        font=italic_font,
                        foreground='gray',  # Color of the text
                        anchor='w',  # Center the text/image within the available space
                        width=65,  # Width of the label
                        padding=(5, 2),  # Padding around the text/image
                        )  # Use our custom style

input_directory = ttk.Label(root,
                            text="",
                            anchor='w',  # Center the text/image within the available space
                            width=61,  # Width of the label
                            padding=(5, 2),  # Padding around the text/image
                            relief='solid',  # raised, sunken, solid, ridge, groove
                            )  # Use our custom style

save_directory = ttk.Label(root,
                           text="",
                           anchor='w',  # Center the text/image within the available space
                           width=61,  # Width of the label
                           padding=(5, 2),  # Padding around the text/image
                           relief='solid',  # raised, sunken, solid, ridge, groove
                           )  # Use our custom style

img_name = ttk.Label(root,
                     text="",
                     anchor='w',  # Center the text/image within the available space
                     width=40,  # Width of the label
                     padding=(0, 2),  # Padding around the text/image
                     )  # Use our custom style







comp_choices = ["DC Voltage Source",
               "DC V. Source (One Terminal)",
               "AC Voltage Source",
               "DC Current Source",
               "AC Current Source",
               "Ground",
               "Wire Overlap",
               "Resistor",
               "Capacitor",
               "Inductor",
               "Diode",
               "Zener diode",
               "BJT (NPN)",
               "BJT (PNP)",
               "MOSFET (N-Channel)",
               "MOSFET (P-Channel)",
               "Op-Amp"]



comp_select = ttk.Combobox(root, values=comp_choices, width=25)
comp_select.set("Select a component type")

comp_select.bind("<<ComboboxSelected>>", comp_selected)


prev_btn = ttk.Button(root, text="Previous", command=show_prev_image)
next_btn = ttk.Button(root, text="Next", command=show_next_image)
undo_btn = ttk.Button(root, text="Undo", command=undo)

save_btn = ttk.Button(root, text="Save", command=save)

saved_as = ttk.Label(root,
                     text="",
                     font=italic_font,
                     foreground='gray',  # Color of the text
                     # background='white',  # Background color of the label
                     anchor='w',  # Center the text/image within the available space
                     width=70,  # Width of the label
                     padding=(5, 2),  # Padding around the text/image
                     )  # Use our custom style

open_imgs_btn.place(x=30, y=30, width=130)
input_dir_btn.place(x=30, y=65, width=130)
save_dir_btn.place(x=30, y=100, width=130)

open_images.place(x=165, y=31)
input_directory.place(x=165, y=66)
save_directory.place(x=165, y=101)

img_name.place(x=30, y=150)

prev_btn.place(x=30, y=830)
next_btn.place(x=133, y=830)
undo_btn.place(x=575, y=830)

save_btn.place(x=720, y=830)
saved_as.place(x=825, y=831)

#app_name.place(x=840, y=25)
comp_select.place(x=440, y=33)



# Defining input notebook and canvases

# Create the notebook widget
notebook_input = ttk.Notebook(root, style='lefttab.TNotebook')
notebook_input.place(x=30, y=152)

# Canvas properties and titles
canvas_configs = comp_terminals


# List to hold canvas references

canvases_in = []


# Create canvases, add to notebook, bind event, and store references
for text in canvas_configs:
    canvas = tk.Canvas(root, width=640, height=640, bg='gray80', relief='sunken', cursor='crosshair', bd=0, highlightthickness=0)
    notebook_input.add(canvas, text=f'  {text}  ')
    canvas.bind("<Button-1>", on_canvas_click)
    canvases_in.append(canvas)


notebook_input.bind("<<NotebookTabChanged>>", on_tab_selected)




# Defining output notebooks and canvases

# List to store notebook references
notebooks_out = []

# List to store canvas lists for each notebook
canvas_out_lists = []

# Names and backgrounds for each type of canvas
canvas_types = [
    ('Gaussian Heatmap', 'gray80'),
    ('Heatmap Overlay', 'gray80'),
    ('Grayscale Output', 'black')
]

# Create notebooks and canvases
for i in range(no_of_terminals):
    # Create a notebook widget
    notebook = ttk.Notebook(root)
    notebook.place(x=720, y=152)  # Adjust placement for illustration; might need adjustment

    # List to hold canvases for this notebook
    canvases = []

    # Create canvases for each type
    for name, bg in canvas_types:
        canvas = tk.Canvas(root, width=640, height=640, bg=bg, relief='sunken', bd=0, highlightthickness=0)
        notebook.add(canvas, text=f' {name} ')
        canvases.append(canvas)

    # Select the 'Heatmap Overlay' by default
    notebook.select(canvases[1])

    # Store the notebook and canvas list
    notebooks_out.append(notebook)
    canvas_out_lists.append(canvases)



# Force the event to run once at startup to ensure proper initial state
root.after(100, lambda: on_tab_selected(None))

img_name.lift()


root.mainloop()
