import pygame

SKIN_OPTIONS = [
    {"label": "Emerald", "body": (66, 184, 118), "head": (230, 255, 190)},
    {"label": "Violet", "body": (156, 79, 198), "head": (244, 194, 255)},
    {"label": "Sunset", "body": (240, 138, 83), "head": (255, 218, 148)},
]
ARENA_OPTIONS = [
    {"label": "Night", "color": (10, 14, 30)},
    {"label": "Ocean", "color": (14, 45, 88)},
    {"label": "Sand", "color": (105, 95, 70)},
]


def ensure_customization(data):
    """Make sure the profile has customizable skin and arena indices."""
    custom = data.get("customization", {})
    custom.setdefault("skin_index", 0)
    custom.setdefault("arena_index", 0)
    data["customization"] = custom
    return custom


def paint_arena(screen, custom):
    """Fill the screen with the currently selected arena color."""
    arena = ARENA_OPTIONS[custom.get("arena_index", 0) % len(ARENA_OPTIONS)]
    screen.fill(arena["color"])


def show_customization(screen, clock, font, big_font, profile_data):
    custom = ensure_customization(profile_data)
    selected = 0
    options = ["skin_index", "arena_index"]

    while True:
        # Event loop for the customization screen.
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
        screen.blit(title, title.get_rect(center=(400, 80)))

        for idx, key in enumerate(options):
            if key == "skin_index":
                label = f"Snake Skin: {SKIN_OPTIONS[custom['skin_index']]['label']}"
            else:
                label = f"Arena: {ARENA_OPTIONS[custom['arena_index']]['label']}"
            color = (255, 255, 255) if idx == selected else (190, 190, 190)
            screen.blit(font.render(label, True, color), (130, 200 + idx * 60))

        skin = SKIN_OPTIONS[custom["skin_index"]]
        pygame.draw.circle(screen, skin["body"], (600, 260), 40)
        pygame.draw.circle(screen, skin["head"], (600, 230), 18)

        back_text = font.render("ESC to go back", True, (220, 220, 220))
        screen.blit(back_text, (100, 520))

        pygame.display.flip()
        clock.tick(60)
