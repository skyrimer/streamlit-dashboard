import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

from components import (create_config_component, ev_dialog, get_current_values,
                        settings_dialog, solar_dialog, wind_dialog)
from config_setup import init_configs, save_config


def get_rectangle_coords(coordinates):
    """Convert two points to rectangle coordinates (x1, y1, x2, y2)"""
    point1, point2 = coordinates
    x1, y1 = point1
    x2, y2 = point2
    # Ensure we have the correct order for rectangle drawing
    return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


def point_in_rectangle(point, rectangle_coords):
    """Check if a point (x, y) is within a rectangle defined by two corner points"""
    x, y = point
    point1, point2 = rectangle_coords
    x1, y1 = point1
    x2, y2 = point2

    # Get the bounds of the rectangle
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)

    return min_x <= x <= max_x and min_y <= y <= max_y


def check_click_in_regions(click_point, regions):
    """Check which region (if any) contains the clicked point"""
    x, y = click_point

    for region_name, coords in regions.items():
        if point_in_rectangle((x, y), coords):
            return region_name
    return None


init_configs()


st.title("Co-simulation Input Parameters")
create_config_component()
st.divider()

# Initialize session state for coordinates
if "coordinates" not in st.session_state:
    st.session_state["coordinates"] = None

# Load and prepare the image
size = (700, 700)
img = Image.open("power.jpg").resize(size, Image.Resampling.LANCZOS)
draw = ImageDraw.Draw(img)

# Define coordinate lists for different components
settings_coordinates = [(240, 345), (465, 125)]
ev_coordinates = [(440, 525), (590, 355)]
wind_coordinates = [(480, 310), (670, 30)]
solar_coordinates = [(60, 230), (240, 70)]

# Create a dictionary for easy region checking
regions = {
    "Settings": settings_coordinates,
    "EV": ev_coordinates,
    "Wind": wind_coordinates,
    "Solar": solar_coordinates
}

# Settings rectangle (blue)
coords = get_rectangle_coords(settings_coordinates)
draw.rectangle(coords, fill=None, outline="blue", width=2)
coords = get_rectangle_coords(ev_coordinates)
draw.rectangle(coords, fill=None, outline="green", width=2)
coords = get_rectangle_coords(wind_coordinates)
draw.rectangle(coords, fill=None, outline="orange", width=2)
coords = get_rectangle_coords(solar_coordinates)
draw.rectangle(coords, fill=None, outline="yellow", width=2)

st.info("💡 **Instructions:** Click within a colored rectangle to detect the region, or click and drag to draw a new rectangle.")
clicked_coordinates = streamlit_image_coordinates(
    img, key="rectangle", width=size[0], height=size[1])

# Handle user interaction
if clicked_coordinates is not None:
    if "x" in clicked_coordinates and "y" in clicked_coordinates and not st.session_state.get("clicked_region") == clicked_coordinates:
        st.session_state.clicked_region = clicked_coordinates
        click_point = (clicked_coordinates["x"], clicked_coordinates["y"])
        clicked_region = check_click_in_regions(click_point, regions)

        if clicked_region:
            if clicked_region == "Settings":
                settings_dialog()
            elif clicked_region == "EV":
                ev_dialog()
            elif clicked_region == "Wind":
                wind_dialog()
            elif clicked_region == "Solar":
                solar_dialog()

st.divider()

# Get current values for save and simulation
(turbines, solar_panels, ev_cars, storage_capacity, grid_capacity,
 initial_money, price_high, price_low, config_name) = get_current_values()

if st.button("Save Configuration"):
    if config_name:
        save_config(turbines, solar_panels, ev_cars,
                    storage_capacity, grid_capacity,
                    initial_money, price_high, price_low)
    else:
        st.error("Please set a configuration name in the Settings dialog first!")
        settings_dialog()

if st.button("Run Simulation", icon="▶️", type="primary"):
    # TODO: Implement the simulation logic
    st.write("Running simulation with current inputs...")
    st.json({
        "turbines": turbines,
        "solar_panels": solar_panels,
        "ev_cars": ev_cars,
        "system_config": {
            "storage_capacity": storage_capacity,
            "grid_capacity": grid_capacity,
            "initial_money": initial_money,
            "price_high": price_high,
            "price_low": price_low,
        }
    })