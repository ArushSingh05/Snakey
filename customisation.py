import pygame
import os

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


def _initialize_arenas():
    # Load arena images with fallback colors if missing
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
    # Ensure all customization keys exist with defaults
    custom = data.get("customization", {})
    custom.setdefault("skin_index", 0)
    custom.setdefault("arena_index", 0)
    data["customization"] = custom
    return custom


def paint_arena(screen, custom):
    # Draw arena background image or fallback color
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
    # Customization menu to select snake skins and arenas
    custom = ensure_customization(profile_data)
    selected = 0
    options = ["skin_index", "arena_index"]

    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
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

        paint_arena(screen, custom)
        title = big_font.render("Customization", True, (245, 245, 245))
        screen.blit(title, title.get_rect(center=(screen_width // 2, 80)))

        for idx, key in enumerate(options):
            if key == "skin_index":
                label = f"Snake Skin: {SKIN_OPTIONS[custom['skin_index']]['label']}"
            else:
                label = f"Arena: {ARENA_OPTIONS[custom['arena_index']]['label']}" if ARENA_OPTIONS else "Arena: (Loading...)"
            color = (255, 255, 255) if idx == selected else (190, 190, 190)
            screen.blit(font.render(label, True, color), (130, 200 + idx * 60))
        
        skin = SKIN_OPTIONS[custom["skin_index"]]
        pygame.draw.circle(screen, skin["body"], (600, 260), 40)
        pygame.draw.circle(screen, skin["head"], (600, 230), 18)

        back_text = font.render("ESC to go back", True, (220, 220, 220))
        screen.blit(back_text, (100, screen_height - 80))

        pygame.display.flip()
        clock.tick(60)
