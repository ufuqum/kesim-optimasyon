from typing import List, Dict, Any, NamedTuple, Optional
import optuna

class Part(NamedTuple):
    length: float
    quantity: int
    name: Optional[str] = None
    cut_order: Optional[int] = None
    cut_type: Optional[str] = None

def _validate_parts(parts_data: List[Part]) -> None:
    if not parts_data:
        raise ValueError("Parça listesi boş olmamalı.")
    for part in parts_data:
        if part.length <= 0 or part.quantity <= 0:
            raise ValueError("Geçersiz parça özellikleri.")

def _simple_first_fit(parts_data: List[Part], stock_length: int, kerf: int) -> List[List[Part]]:
    sorted_parts = sorted(parts_data, key=lambda p: p.length, reverse=True)
    stocks: List[List[Part]] = []
    lengths_in_stocks: List[float] = []

    for part in sorted_parts:
        for _ in range(part.quantity):
            length_needed = part.length + kerf
            placed = False
            for idx, current_length in enumerate(lengths_in_stocks):
                if current_length + length_needed <= stock_length:
                    stocks[idx].append(part)
                    lengths_in_stocks[idx] += length_needed
                    placed = True
                    break
            if not placed:
                stocks.append([part])
                lengths_in_stocks.append(length_needed)
    return stocks

def calculate_fire_and_efficiency(plan: List[List[Part]], stock_length: int, kerf: int) -> dict:
    total_stocks = len(plan)
    total_material = total_stocks * stock_length
    total_used = 0

    stock_fire = []
    stock_efficiency = []

    for stock_parts in plan:
        length_sum = sum(p.length for p in stock_parts)
        total_kerf = kerf * (len(stock_parts) - 1) if len(stock_parts) > 1 else 0
        used = length_sum + total_kerf
        fire = stock_length - used
        efficiency = (length_sum / stock_length) * 100 if stock_length > 0 else 0
        stock_fire.append(fire)
        stock_efficiency.append(efficiency)
        total_used += used

    total_fire = total_material - total_used
    total_efficiency = (total_used / total_material) * 100 if total_material > 0 else 0

    return {
        "total_fire": total_fire,
        "total_efficiency": total_efficiency,
        "stock_fire": stock_fire,
        "stock_efficiency": stock_efficiency,
    }

def calculate_costs(fire_info: dict, stock_unit_price: float) -> dict:
    total_fire = fire_info.get("total_fire", 0)
    total_stocks = len(fire_info.get("stock_fire", []))
    total_cost = total_stocks * stock_unit_price
    fire_cost = total_fire * stock_unit_price
    savings = 0
    return {
        "total_cost": total_cost,
        "fire_cost": fire_cost,
        "savings": savings,
    }

def optimize_parts(parts_data: List[Dict[str, Any]], stock_length: int, kerf: int,
                   trials: int = 20, algorithm: str = "first_fit",
                   kerf_min: Optional[int] = None,
                   kerf_max: Optional[int] = None) -> Dict[str, Any]:
    wrapped_parts = []
    for p in parts_data:
        wrapped_parts.append(Part(
            length=float(p["length"]),
            quantity=int(p["quantity"]),
            name=p.get("name"),
            cut_order=p.get("cut_order"),
            cut_type=p.get("cut_type"),
        ))

    _validate_parts(wrapped_parts)

    k_min = kerf_min if kerf_min is not None else max(1, kerf - 1)
    k_max = kerf_max if kerf_max is not None else kerf + 2
    if k_min > k_max:
        raise ValueError("kerf_min kerf_max'dan büyük olamaz")

    def objective(trial: optuna.Trial) -> int:
        trial_kerf = trial.suggest_int("kerf", k_min, k_max)
        plan = _simple_first_fit(wrapped_parts, stock_length, trial_kerf)
        return len(plan)

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=trials)

    best_kerf = study.best_params["kerf"]
    best_plan = _simple_first_fit(wrapped_parts, stock_length, best_kerf)

    fire_eff = calculate_fire_and_efficiency(best_plan, stock_length, best_kerf)

    return {
        "kerf": best_kerf,
        "plan": best_plan,
        "used_stocks": len(best_plan),
        "optuna_study": study,
        "fire_efficiency": fire_eff,
        "parts_list": parts_data,
    }

def draw_cutting_plan(ax, canvas, optimization_result, stock_length: int = None, kerf: int = None):
    import matplotlib.patches as patches
    ax.clear()

    used_stocks = optimization_result.get("used_stocks", 0)
    kerf_val = kerf or optimization_result.get("kerf", 0)

    title = f"Kesim Planı (Kullanılan Stok Sayısı: {used_stocks}, Kerf: {kerf_val} mm)"
    ax.set_title(title)
    ax.set_xlabel("Uzunluk (mm)")
    ax.set_ylabel("Stok Parça No")

    stock_length_val = stock_length or 6000
    plan = optimization_result.get("plan", [])

    y_height = 7
    y_gap = 12

    colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#c2f0c2", "#ffb3e6"]

    for stock_idx, stock_parts in enumerate(plan):
        current_x = 0
        y_bottom = stock_idx * (y_height + y_gap)
        sorted_parts = sorted(stock_parts, key=lambda p: p.cut_order if p.cut_order is not None else 0)
        for part_idx, part in enumerate(sorted_parts):
            part_length = part.length
            color = colors[part_idx % len(colors)]
            rect = patches.Rectangle(
                (current_x, y_bottom), part_length, y_height,
                edgecolor="black", facecolor=color
            )
            ax.add_patch(rect)
            label = f"{part.name}\n{part_length:.1f} mm"
            if part.cut_type and part.cut_type.lower() != "düz kesim":
                label += f"\n{part.cut_type}"
            ax.text(current_x + part_length / 2, y_bottom + y_height / 2, label,
                    ha="center", va="center", fontsize=8)
            current_x += part_length + kerf_val

        ax.plot([0, stock_length_val], [y_bottom - 1, y_bottom - 1], "k--", linewidth=0.5)

    ax.set_xlim(0, stock_length_val + 150)
    ax.set_ylim(-15, len(plan) * (y_height + y_gap))
    ax.grid(True)
    try:
        canvas.draw()
    except Exception:
        pass
