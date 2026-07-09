import pygame
import os
from fonts import get_font
from ui_helpers import draw_transparent_panel

# Skin options.
SKIN_OPTIONS = [
    {"label": "Emerald", "body": (66, 184, 118), "head": (230, 255, 190)},
    {"label": "Violet", "body": (156, 79, 198), "head": (244, 194, 255)},
    {"label": "Sunset", "body": (240, 138, 83), "head": (255, 218, 148)},
]

ARENA_IMAGE_PATHS = [
    {"label": "Ocean", "file": "images/arena/arena0.png"},
    {"label": "Sunset", "file": "images/arena/arena1.png"},
    {"label": "Peak", "file": "images/arena/arena2.png"},
]
TITLE_COLOR = (20, 30, 60)

def _initialize_arenas():
    arenas = []
    for arena in ARENA_IMAGE_PATHS:
        try:
            if os.path.exists(arena["file"]):
                img = pygame.image.load(arena["file"])
                arenas.append({"label": arena["label"], "image": img})
            else:
                print(f"Warning: {arena['file']} not found, using fallback color")
                arenas.append({"label": arena["label"], "image": None, "color": (30, 30, 30)})
        except Exception as e:
            print(f"Error loading {arena['file']}: {e}")
            arenas.append({"label": arena["label"], "image": None, "color": (30, 30, 30)})
    return arenas

ARENA_OPTIONS = _initialize_arenas()

def ensure_customization(data):
    custom = data.get("customization", {})
    custom.setdefault("skin_index", 0)
    custom.setdefault("arena_index", 0)
    data["customization"] = custom
    return custom

def paint_arena(screen, custom_or_profile):
    # Accept either a custom dict or a profile dict
    if isinstance(custom_or_profile, dict) and "customization" in custom_or_profile:
        custom = custom_or_profile["customization"]
    else:
        custom = custom_or_profile

    if not ARENA_OPTIONS:
        screen.fill((30, 30, 30))
        return

    arena = ARENA_OPTIONS[custom.get("arena_index", 0) % len(ARENA_OPTIONS)]
    image = arena.get("image")

    if image:
        scaled_image = pygame.transform.scale(image, screen.get_size())
        screen.blit(scaled_image, (0, 0))
    else:
        color = arena.get("color", (30, 30, 30))
        screen.fill(color)

def show_customisation(screen, clock, font, big_font, profile_data):
    custom = ensure_customization(profile_data)
    selected = 0
    options = ["skin_index", "arena_index"]

    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        title_font_dyn = get_font(max(36, min(64, int(screen_height * 0.12))))
        custom_font = get_font(max(18, min(28, int(screen_height * 0.07))))
        button_font = get_font(max(14, min(24, int(screen_height * 0.055))))

        back_button_width = max(100, int(screen_width * 0.15))
        back_button_height = max(35, int(screen_height * 0.08))
        back_rect = pygame.Rect(int(screen_width * 0.05), screen_height - back_button_height - 20, back_button_width, back_button_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.VIDEORESIZE:
                new_width = max(event.size[0], 320)
                new_height = max(event.size[1], 240)
                if new_width != event.size[0] or new_height != event.size[1]:
                    screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_UP:
                    selected = max(0, selected - 1)
                if event.key == pygame.K_DOWN:
                    selected = min(len(options) - 1, selected + 1)
                if event.key == pygame.K_LEFT:
                    if options[selected] == "skin_index":
                        custom["skin_index"] = (custom["skin_index"] - 1) % len(SKIN_OPTIONS)
                    else:
                        custom["arena_index"] = (custom["arena_index"] - 1) % len(ARENA_OPTIONS)
                if event.key == pygame.K_RIGHT:
                    if options[selected] == "skin_index":
                        custom["skin_index"] = (custom["skin_index"] + 1) % len(SKIN_OPTIONS)
                    else:
                        custom["arena_index"] = (custom["arena_index"] + 1) % len(ARENA_OPTIONS)
                if event.key == pygame.K_RETURN:
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "menu"

        paint_arena(screen, custom)

        title = title_font_dyn.render("Customization", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(screen_width // 2, int(screen_height * 0.1))))

        # centered panel
        panel_top = int(screen_height * 0.2)
        panel_bottom = int(screen_height * 0.65)
        panel_width = screen_width - int(screen_width * 0.20)
        panel_x = (screen_width - panel_width) // 2
        panel_height = panel_bottom - panel_top
        draw_transparent_panel(screen, panel_x, panel_top, panel_width, panel_height, radius=20)

        # Options centered inside panel
        option_y = panel_top + int(panel_height * 0.12)
        option_spacing = int(panel_height * 0.2)
        for idx, key in enumerate(options):
            if key == "skin_index":
                label = f"Snake Skin: {SKIN_OPTIONS[custom['skin_index']]['label']}"
            else:
                label = f"Arena: {ARENA_OPTIONS[custom['arena_index']]['label']}" if ARENA_OPTIONS else "Arena: (Loading...)"
            color = (255, 255, 255) if idx == selected else (190, 190, 190)
            label_surf = custom_font.render(label, True, color)
            label_x = panel_x + (panel_width - label_surf.get_width()) // 2
            screen.blit(label_surf, (label_x, option_y + idx * option_spacing))

        # Preview centered inside the right half of panel
        skin = SKIN_OPTIONS[custom["skin_index"]]
        preview_radius = max(30, int(screen_width * 0.05))
        preview_x = panel_x + panel_width // 2
        preview_y = panel_top + int(panel_height * 0.7)
        pygame.draw.circle(screen, skin["body"], (preview_x, preview_y), preview_radius)
        pygame.draw.circle(screen, skin["head"], (preview_x, preview_y - int(preview_radius * 0.5)), max(15, int(preview_radius * 0.5)))

        hint = button_font.render("Use UP/DOWN to switch, LEFT/RIGHT to change", True, (210, 225, 255))
        hint_x = panel_x + (panel_width - hint.get_width()) // 2
        screen.blit(hint, (hint_x, panel_top + int(panel_height * 0.86)))

        pygame.draw.rect(screen, (70, 130, 180), back_rect, border_radius=20)
        back_label = button_font.render("Back", True, (255, 255, 255))
        screen.blit(back_label, back_label.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(60)