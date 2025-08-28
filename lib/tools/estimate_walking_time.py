def estimate_walking_time(distance_km: float, walking_speed_kmph: float = 5.0, hours_per_day: float = 8.0, rest_days_per_week: float = 1.0) -> dict:
    """
    Estimate time to walk a given distance based on walking speed and daily walking hours.

    Parameters:
      distance_km: Distance to walk in kilometers (required).
      walking_speed_kmph: Average sustained walking speed in km/h. Default 5.
      hours_per_day: Number of hours walking per day. Default 8.
      rest_days_per_week: Planned rest days per week. Default 1.

    Returns:
      A dictionary with:
        - total_hours: Total walking hours required.
        - total_days_continuous: Number of continuous days (including fractional day) if walking every day.
        - estimated_days_with_rest: Estimated calendar days, accounting for rest days.
        - daily_distance_km: Distance covered per walking day.
        - summary: Human-readable summary of the results.
    """
    # Basic validation
    if distance_km < 0:
        raise ValueError("distance_km must be non-negative.")
    if walking_speed_kmph <= 0:
        raise ValueError("walking_speed_kmph must be greater than zero.")
    if hours_per_day <= 0:
        raise ValueError("hours_per_day must be greater than zero.")
    if rest_days_per_week < 0:
        raise ValueError("rest_days_per_week cannot be negative.")

    total_hours = distance_km / walking_speed_kmph
    daily_distance_km = walking_speed_kmph * hours_per_day

    # Continuous days if walking every day
    total_days_continuous = total_hours / hours_per_day if hours_per_day > 0 else 0.0

    # Walking days per week and weekly walking hours considering rest days
    workdays_per_week = 7.0 - rest_days_per_week
    if workdays_per_week <= 0:
        raise ValueError("rest_days_per_week leaves no walking days in a week.")

    weekly_walking_hours = hours_per_day * workdays_per_week

    weeks_needed = total_hours / weekly_walking_hours if weekly_walking_hours > 0 else float('inf')
    estimated_days_with_rest = weeks_needed * 7.0

    summary = (
        f"Distance: {distance_km:.2f} km, Speed: {walking_speed_kmph:.2f} km/h, "
        f"Hours per day: {hours_per_day:.2f}, Rest days/week: {rest_days_per_week:.2f}. "
        f"Total walking hours: {total_hours:.2f}. "
        f"Daily distance (per walking day): {daily_distance_km:.2f} km. "
        f"Continuous days (walking daily): {total_days_continuous:.2f} days. "
        f"Estimated calendar days with rest: {estimated_days_with_rest:.2f} days."
    )

    return {
        "total_hours": total_hours,
        "total_days_continuous": total_days_continuous,
        "estimated_days_with_rest": estimated_days_with_rest,
        "daily_distance_km": daily_distance_km,
        "summary": summary
    }