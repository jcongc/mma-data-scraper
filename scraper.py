"""
    Scraper Module

    This module runs a script that takes in inputs for which fighter the user wants stats for.
    The user can also choose which type of statistics they'd like.
"""

import re
import gc
import pandas as pd
from tabulate import tabulate
from fighter import FighterData

# Glossary texts
STRIKING_GLOSSARY = """
Glossary for Striking:
- %BODY: Target Breakdown Body
- %HEAD: Target Breakdown Head
- %LEG: Target Breakdown Leg
- SDBL/A: Significant Distance Body Strikes Landed-Significant Distance Body Strike Attempts
- SDHL/A:Significant Distance Head Strikes Landed-Significant Distance Head Strike Attempts
- SDLL/A:Significant Distance Leg Strikes Landed-Significant Distance Leg Strike Attempts
- TSL:Total Strikes Landed
- TSA:Total Strikes Attempts
- SSA:Significant Strikes Attempts
- SSL:Significant Strikes Landed
- TSL-TSA:Total Strikes Landed-Total Strikes Attempts
- KD: Knockdowns
"""

CLINCH_GLOSSARY = """
Glossary for Clinch:
- SCBL: Significant Clinch Body Strikes Landed
- SCBA: Significant Clinich Body Strike Attempts
- SCHL: Significant Clinch Head Strikes Landed
- SCHA: Significant Clinch Head Strike Attempts
- SCLL: Significant Clinch Leg Strikes Landed
- SCLA: Significant Clinch Leg Strike Attempts
- RV: Reversals
- SR: Slam Rate
- TDL: Takedowns Landed
- TDA: Takedowns Attempted
- TDS: Takedowns Slams
- TK ACC: Takedown Accuracy
"""

GROUND_GLOSSARY = """
Glossary for Ground:
- SGBL: Significant Ground Body Strikes Landed
- SGBA: Significant Ground Body Strike Attempts
- SGHL: Significant Ground Head Strikes Landed
- SGHA: Significant Ground Head Strike Attempts
- SGLL: Significant Ground Leg Strikes Landed
- SGLA: Significant Ground Leg Strikes Attempted
- AD: Advances
- ADTB: Advance To Back
- ADHG: Advance To Half Guard
- ADTM: Advance To Mount
- ADTS: Advance To Side
- SM: Submissions
"""

def get_fighter_input():
    """Takes in the fighter ID"""
    user_input = input("Please enter a fighter id or their ESPN URL: ")
    return user_input

def get_new_fighter():
    """Takes in new fighter ID"""
    user_input = input("Please enter fighter id or their ESPN URL (Type 'b' to go back): ")
    return user_input

def create_fighter_instance(user_input):
    """Creates an instance of a fighter"""
    fighter = FighterData()
    if re.match(r'^\d+$', user_input):
        fighter.set_url_from_id(user_input)
    elif re.match(r'^(https?://(www.)?)?espn\.com/mma/fighter/_/id/\d+(/[\w-]+)?$', user_input):
        fighter.set_url_from_page(user_input)
    else:
        print("Invalid input. Please enter a fighter id or an ESPN URL.")
        return None
    fighter.set_resource()
    fighter.set_soup()
    return fighter

def print_fighter_info(fighter):
    """Prints the basic fighter information"""
    opponents = fighter.get_opponents()
    results = fighter.get_results()
    methods = fighter.get_methods()
    end_round = fighter.get_round()
    time = fighter.get_time()
    event = fighter.get_event()
    records = fighter.get_record()
    fighter_name = fighter.get_name()
    print(fighter_name)
    print(f"Record: {records[0]}")
    print(f"TKO/KO: {records[1]}")
    print(f"Submissions: {records[2]}\n")
    fight_history_df = pd.DataFrame({
        "Opponent": opponents,
        "Result": results,
        "Method": methods,
        "Round": end_round,
        "Time": time,
        "Event": event
    })
    print(
        tabulate(
            fight_history_df,
            showindex=False,
            headers=fight_history_df.columns))

def print_stat_type(fighter, stat_type):
    """Takes in an input of which type of statistic they'd like and prints it."""
    if stat_type.lower() == "s":
        striking_headings, striking_stats = fighter.get_striking()
        striking_df = pd.DataFrame(striking_stats, columns=striking_headings)
        print("\n")
        print("Table of All Striking Stats")
        print(tabulate(striking_df, showindex=False, headers=striking_headings))
        print("\n")
        avg_striking_df = pd.DataFrame(fighter.find_column_avg(striking_stats),
                                       index=striking_headings).T
        print("Average Striking Stats")
        print(tabulate(avg_striking_df, showindex=False, headers=striking_headings))
        print("\n")
    elif stat_type.lower() == "c":
        clinch_headings, clinch_stats = fighter.get_clinch()
        clinch_df = pd.DataFrame(clinch_stats, columns=clinch_headings)
        print("\n")
        print("Table of All Clinch Stats")
        print(tabulate(clinch_df, showindex=False, headers=clinch_headings))
        print("\n")
        avg_clinch_df = pd.DataFrame(fighter.find_column_avg(clinch_stats), index=clinch_headings).T
        print("Average Clinch Stats")
        print(tabulate(avg_clinch_df, showindex=False, headers=clinch_headings))
        print("\n")
    elif stat_type.lower() == "g":
        ground_headings, ground_stats = fighter.get_ground()
        ground_df = pd.DataFrame(ground_stats, columns=ground_headings)
        print("\n")
        print("Table of All Ground Stats")
        print(tabulate(ground_df, showindex=False, headers=ground_headings))
        print("\n")
        avg_ground_df = pd.DataFrame(fighter.find_column_avg(ground_stats), index=ground_headings).T
        print("Average Ground Stats")
        print(tabulate(avg_ground_df, showindex=False, headers=ground_headings))
        print("\n")
    elif stat_type.lower() == "gl":
        glossary_type = input(
            "Choose a glossary: \n"
            "'s' - Striking\n"
            "'c' - Clinch\n"
            "'g' - Ground\n"
            "'a' - All\n"
            "'b' - Back\n"
            "> "
        ).upper()
        if glossary_type.lower() == "s":
            print(STRIKING_GLOSSARY)
        elif glossary_type.lower() == "c":
            print(CLINCH_GLOSSARY)
        elif glossary_type.lower() == "g":
            print(GROUND_GLOSSARY)
        elif glossary_type.lower() == "a":
            print(STRIKING_GLOSSARY)
            print(CLINCH_GLOSSARY)
            print(GROUND_GLOSSARY)
        elif glossary_type.lower() == "b":
            print("Returning to menu.")
        else:
            print(
                "Invalid glossary type. Please choose 'striking', 'clinch', or 'ground'.")

def main():
    """Main function which runs the script"""
    user_input = get_fighter_input()
    fighter = create_fighter_instance(user_input)
    if fighter is None:
        return
    print_fighter_info(fighter)
    while True:
        stat_type = input(
            "Choose an option: \n"
            "'s' Striking stats\n"
            "'c' Clinch stats\n"
            "'g' Ground stats\n"
            "'gl' - Glossary\n"
            "'cf' - Change Fighter\n"
            "'e' - Exit\n"
            "> "
        )
        if stat_type.lower() == "e":
            print("Exiting. Thanks for using my data scraper!")
            break
        if stat_type.lower() == "cf":
            new_input = get_new_fighter()
            if new_input.lower() != "b":
                del fighter
                gc.collect()
                fighter = create_fighter_instance(new_input)
                print_fighter_info(fighter)
        elif stat_type.lower() not in ["s", "c", "g", "gl"]:
            print("Invalid input. Please choose a valid stat type, 'glossary', or 'exit'.")
        else:
            print_stat_type(fighter, stat_type)

if __name__ == "__main__":
    main()
