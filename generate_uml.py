"""
Generates uml_original.png and uml_updated.png using only Pillow.
Run: python generate_uml.py
"""
from PIL import Image, ImageDraw, ImageFont
import math

# ── Palette ───────────────────────────────────────────────────────────────────
BG          = (245, 247, 250)
HDR_BG      = (44,  62,  80)
HDR_TXT     = (255, 255, 255)
ATTR_BG     = (236, 240, 245)
MTH_BG      = (255, 255, 255)
BODY_TXT    = (30,  40,  55)
BORDER      = (100, 120, 145)
DIV         = (180, 195, 210)
ARROW       = (70,  100, 135)
TITLE_CLR   = (25,  45,  75)

# ── Geometry ──────────────────────────────────────────────────────────────────
BOX_W    = 310
HDR_H    = 38
ROW_H    = 21
PAD      = 12       # text left-padding inside box
GAP_X    = 60       # horizontal gap between boxes
GAP_Y    = 70       # vertical gap between rows

# ── Font loading ──────────────────────────────────────────────────────────────
def _font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.dfont",
        "/Library/Fonts/Courier New Bold.ttf" if bold else "/Library/Fonts/Courier New.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

F_TITLE  = _font(15, bold=True)
F_HDR    = _font(13, bold=True)
F_BODY   = _font(11)
F_REL    = _font(10)
F_MAIN   = _font(18, bold=True)

# ── Class data ────────────────────────────────────────────────────────────────

OLD_CLASSES = [
    {
        "name": "Owner",
        "attrs": [
            "- ownerName : String",
            "- dateOfBirth : Date",
            "- age : Int",
            "- availability : String",
            "- preferences : String",
        ],
        "methods": [
            "+ modifyOwner()",
        ],
    },
    {
        "name": "Pet",
        "attrs": [
            "- petName : String",
            "- dateOfBirth : Date",
            "- age : Int",
            "- species : String",
            "- breed : String",
        ],
        "methods": [
            "+ addPet()",
            "+ modifyPet()",
            "+ removePet()",
        ],
    },
    {
        "name": "Task",
        "attrs": [
            "- taskName : String",
            "- ownerName : String",
            "- petName : String",
            "- priority : String",
            "- scheduledDate : Date",
            "- scheduledStartTime : Time",
            "- scheduledEndTime : Time",
            "- duration : Duration",
        ],
        "methods": [
            "+ addTask()",
            "+ modifyTask()",
            "+ removeTask()",
        ],
    },
    {
        "name": "Plan",
        "attrs": [
            "- date : Date",
            "- taskList : List<Task>",
        ],
        "methods": [
            "+ viewPlan()",
            "+ modifyPlan()",
            "+ removePlan()",
        ],
    },
]

OLD_RELATIONS = [
    ("Owner", "Pet",  "1", "*", "owns"),
    ("Owner", "Task", "1", "*", "schedules"),
    ("Pet",   "Task", "1", "*", "assigned to"),
    ("Plan",  "Task", "1", "*", "contains"),
]

NEW_CLASSES = [
    {
        "name": "PawPalSystem",
        "attrs": [
            "- owners : Dict<str, Owner>",
            "- pets : Dict<str, Pet>",
            "- tasks : Dict<str, Task>",
            "- plans : Dict<str, Scheduler>",
        ],
        "methods": [
            "+ add_owner(owner)",
            "+ add_pet(pet, owner_id)",
            "+ add_task(task)",
            "+ add_plan(plan)",
            "+ remove_owner(owner_id)",
            "+ remove_pet(pet_id)",
            "+ remove_task(task_id)",
            "+ remove_plan(plan_id)",
            "+ get_tasks_by_pet(pet_id)",
            "+ get_tasks_by_status(completed)",
            "+ filter_tasks(pet_name, completed)",
            "+ complete_task(task_id) : Task",
            "+ generate_recurring_tasks(...)",
            "+ create_plan(owner_id, date)",
        ],
    },
    {
        "name": "Owner",
        "attrs": [
            "- owner_id : str",
            "- owner_name : str",
            "- date_of_birth : date",
            "- age : int",
            "- availability : str",
            "- preferences : str",
            "- pets : List<Pet>",
            "- tasks : List<Task>",
            "- plans : List<Scheduler>",
        ],
        "methods": [
            "+ modify_owner()",
            "+ add_pet(pet)",
            "+ remove_pet(pet_id)",
            "+ get_availability_window()",
            "+ get_all_tasks()",
            "+ get_tasks_sorted_by_time()",
            "+ get_tasks_by_pet(pet_id)",
            "+ get_tasks_by_status(completed)",
        ],
    },
    {
        "name": "Pet",
        "attrs": [
            "- pet_id : str",
            "- pet_name : str",
            "- date_of_birth : date",
            "- age : int",
            "- species : str",
            "- breed : str",
            "- tasks : List<Task>",
        ],
        "methods": [
            "+ modify_pet()",
            "+ add_task(task)",
        ],
    },
    {
        "name": "Task",
        "attrs": [
            "- task_id : str",
            "- description : str",
            "- owner_id : str",
            "- pet_id : str",
            "- priority : str",
            "- scheduled_date : date",
            "- scheduled_start_time : time",
            "- scheduled_end_time : time",
            "- duration : timedelta",
            "- frequency : str",
            "- completion_status : bool",
        ],
        "methods": [
            "+ modify_task()",
            "+ mark_complete()",
            "+ set_schedule(start_time)",
            "+ get_effective_priority(...) : int",
            "+ validate_times() : bool",
        ],
    },
    {
        "name": "Scheduler",
        "attrs": [
            "- scheduler_id : str",
            "- date : date",
            "- owner_id : str",
            "- tasks : List<Task>",
            "- explanations : List<str>",
        ],
        "methods": [
            "+ view_plan() : List<Task>",
            "+ sort_by_time(tasks)",
            "+ get_explanations()",
            "+ add_task(task, reason)",
            "+ remove_task(task_id)",
            "+ modify_plan(tasks)",
            "+ remove_plan()",
            "+ validate_schedule(new_task)",
            "+ detect_conflicts()",
            "+ get_conflict_warnings()",
        ],
    },
]

NEW_RELATIONS = [
    ("PawPalSystem", "Owner",     "1", "*", "manages"),
    ("PawPalSystem", "Pet",       "1", "*", "tracks"),
    ("PawPalSystem", "Task",      "1", "*", "tracks"),
    ("PawPalSystem", "Scheduler", "1", "*", "manages"),
    ("Owner",        "Pet",       "1", "*", "owns"),
    ("Owner",        "Task",      "1", "*", "schedules"),
    ("Pet",          "Task",      "1", "*", "assigned to"),
    ("Scheduler",    "Task",      "1", "*", "contains"),
]


# ── Drawing helpers ───────────────────────────────────────────────────────────

def box_height(cls):
    return HDR_H + (len(cls["attrs"]) + len(cls["methods"]) + 1) * ROW_H + 6


def draw_class_box(draw, x, y, cls):
    """Draw one UML class box; return (x, y, w, h) of the bounding rect."""
    h = box_height(cls)

    # Drop shadow
    shadow_off = 4
    draw.rectangle(
        [x + shadow_off, y + shadow_off, x + BOX_W + shadow_off, y + h + shadow_off],
        fill=(200, 210, 220),
    )

    # Header
    draw.rectangle([x, y, x + BOX_W, y + HDR_H], fill=HDR_BG, outline=BORDER, width=1)
    draw.text(
        (x + BOX_W // 2, y + HDR_H // 2),
        cls["name"],
        font=F_HDR,
        fill=HDR_TXT,
        anchor="mm",
    )

    cur_y = y + HDR_H

    # Attribute rows
    for attr in cls["attrs"]:
        draw.rectangle([x, cur_y, x + BOX_W, cur_y + ROW_H], fill=ATTR_BG, outline=DIV, width=1)
        draw.text((x + PAD, cur_y + ROW_H // 2), attr, font=F_BODY, fill=BODY_TXT, anchor="lm")
        cur_y += ROW_H

    # Divider
    draw.rectangle([x, cur_y, x + BOX_W, cur_y + 3], fill=BORDER, outline=BORDER, width=1)
    cur_y += 3

    # Method rows
    for mth in cls["methods"]:
        draw.rectangle([x, cur_y, x + BOX_W, cur_y + ROW_H], fill=MTH_BG, outline=DIV, width=1)
        draw.text((x + PAD, cur_y + ROW_H // 2), mth, font=F_BODY, fill=BODY_TXT, anchor="lm")
        cur_y += ROW_H

    # Outer border
    draw.rectangle([x, y, x + BOX_W, y + h], outline=BORDER, width=2)

    return (x, y, BOX_W, h)


def center_of(rect):
    x, y, w, h = rect
    return x + w // 2, y + h // 2


def draw_arrow(draw, src_rect, dst_rect, label="", mult_src="1", mult_dst="*"):
    """Draw a simple labelled arrow from src to dst box."""
    sx, sy, sw, sh = src_rect
    dx, dy, dw, dh = dst_rect

    sc = (sx + sw // 2, sy + sh // 2)
    dc = (dx + dw // 2, dy + dh // 2)

    # Pick the closest edge midpoints
    def edge_points(rx, ry, rw, rh):
        return {
            "top":    (rx + rw // 2, ry),
            "bottom": (rx + rw // 2, ry + rh),
            "left":   (rx, ry + rh // 2),
            "right":  (rx + rw, ry + rh // 2),
        }

    se = edge_points(*src_rect)
    de = edge_points(*dst_rect)

    best, best_d = ("right", "left"), 1e9
    for sk, sp in se.items():
        for dk, dp in de.items():
            d = math.hypot(sp[0] - dp[0], sp[1] - dp[1])
            if d < best_d:
                best_d = d
                best = (sk, dk)

    p1 = se[best[0]]
    p2 = de[best[1]]

    draw.line([p1, p2], fill=ARROW, width=2)

    # Arrowhead at p2
    angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    aw, ah = 12, 6
    for sign in (1, -1):
        tip = (
            p2[0] - int(aw * math.cos(angle - sign * 0.4)),
            p2[1] - int(aw * math.sin(angle - sign * 0.4)),
        )
        draw.line([p2, tip], fill=ARROW, width=2)

    # Mid-point label
    mx = (p1[0] + p2[0]) // 2
    my = (p1[1] + p2[1]) // 2
    if label:
        draw.text((mx, my - 9), label, font=F_REL, fill=ARROW, anchor="mm")

    # Multiplicity
    draw.text((p1[0] + 6, p1[1] - 9), mult_src, font=F_REL, fill=ARROW, anchor="lm")
    draw.text((p2[0] - 6, p2[1] - 9), mult_dst, font=F_REL, fill=ARROW, anchor="rm")


# ── Layout helpers ────────────────────────────────────────────────────────────

def layout_grid(classes, cols, margin=60):
    """Return {name: (x, y)} positions for a grid layout."""
    positions = {}
    row_heights = []
    for i, cls in enumerate(classes):
        r = i // cols
        while len(row_heights) <= r:
            row_heights.append(0)
        row_heights[r] = max(row_heights[r], box_height(cls))

    for i, cls in enumerate(classes):
        col = i % cols
        row = i // cols
        x = margin + col * (BOX_W + GAP_X)
        y = margin + sum(row_heights[:row]) + row * GAP_Y
        positions[cls["name"]] = (x, y)
    return positions


# ── Render function ───────────────────────────────────────────────────────────

def render(title, classes, relations, positions, output_path):
    # Calculate canvas size
    max_x = max(x + BOX_W for x, _ in positions.values()) + 60
    max_y = max(py + box_height(c) for c in classes
                for name, (px, py) in positions.items() if c["name"] == name) + 80

    img  = Image.new("RGB", (max_x, max_y), BG)
    draw = ImageDraw.Draw(img)

    # Background grid lines (subtle)
    for gx in range(0, max_x, 40):
        draw.line([(gx, 0), (gx, max_y)], fill=(230, 234, 240), width=1)
    for gy in range(0, max_y, 40):
        draw.line([(0, gy), (max_x, gy)], fill=(230, 234, 240), width=1)

    # Draw boxes and collect rects
    rects = {}
    for cls in classes:
        x, y = positions[cls["name"]]
        rects[cls["name"]] = draw_class_box(draw, x, y, cls)

    # Draw relations
    for src, dst, ms, md, lbl in relations:
        if src in rects and dst in rects:
            draw_arrow(draw, rects[src], rects[dst], lbl, ms, md)

    # Title
    draw.text((max_x // 2, 22), title, font=F_MAIN, fill=TITLE_CLR, anchor="mm")

    img.save(output_path)
    print(f"Saved: {output_path}  ({max_x}x{max_y})")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Original UML — 2×2 grid
    old_positions = layout_grid(OLD_CLASSES, cols=2, margin=60)
    render(
        "PawPal+ — Original UML",
        OLD_CLASSES,
        OLD_RELATIONS,
        old_positions,
        "uml_original.png",
    )

    # Updated UML — PawPalSystem top-center, then 4 classes in a row below
    heights     = {c["name"]: box_height(c) for c in NEW_CLASSES}
    top_cls     = NEW_CLASSES[0]   # PawPalSystem
    bottom_cls  = NEW_CLASSES[1:]  # Owner, Pet, Task, Scheduler

    margin      = 60
    total_w     = len(bottom_cls) * BOX_W + (len(bottom_cls) - 1) * GAP_X
    top_x       = margin + (total_w - BOX_W) // 2
    top_y       = margin + 30

    new_positions = {top_cls["name"]: (top_x, top_y)}
    row2_y = top_y + heights[top_cls["name"]] + GAP_Y
    for i, cls in enumerate(bottom_cls):
        new_positions[cls["name"]] = (margin + i * (BOX_W + GAP_X), row2_y)

    render(
        "PawPal+ — Updated UML",
        NEW_CLASSES,
        NEW_RELATIONS,
        new_positions,
        "uml_updated.png",
    )
