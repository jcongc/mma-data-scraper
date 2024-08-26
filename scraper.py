import re
import pandas as pd
from fighter import FighterData
from tabulate import tabulate

def main() -> None:

    # Create an instance of the FighterData class
    fighter = FighterData()

    # Ask the user for a fighter id or their ESPN URL
    user_input = input("Please enter a fighter id or their ESPN URL: ")

    # Check if the user input is a fighter id or an ESPN URL
    if re.match(r'^\d+$', user_input):  # If the user input is a fighter id
        fighter._set_url_from_id(user_input)
    elif re.match(r'^(https?://(www.)?)?espn\.com/mma/fighter/_/id/\d+(/[\w-]+)?$', user_input):  # If the user input is an ESPN URL
        fighter._set_url_from_page(user_input)
    else:
        print("Invalid input. Please enter a fighter id or an ESPN URL.")
        return

    # Set the resource
    
    fighter._set_resource()

    # Set the soup object
    
    fighter._set_soup()

    # Get the opponents
    
    opponents = fighter.get_opponents()

    # Get the results
    
    results = fighter.get_results()

    # Get the method a fight ended
    
    methods = fighter.get_methods()

    # Get the round the fight ended
    
    end_round = fighter.get_round()

    # Get the the time which a fight ended

    time = fighter.get_time()

    # Get the event which the fighter fought at

    event = fighter.get_event()

    records = fighter.get_record()

    fighter_name = fighter.get_name()

    print(fighter_name)
    print(f"Record: {records[0]}")
    print(f"TKO/KO: {records[1]}")
    print(f"Submissions: {records[2]}")
    
    # Create a table with all the results

    fight_history_df = pd.DataFrame({
        "Opponent": opponents,
        "Result": results,
        "Method": methods,
        "Round": end_round,
        "Time": time,
        "Event": event
    })

    print(tabulate(fight_history_df, showindex=False, headers=fight_history_df.columns))

    # Give option to choose what type of statistic they'd like

    while True:
        stat_type = input("Would you like stats for striking, clinch, or ground? (Type 'exit' to quit or 'glossary' for a glossary): ")
        
        if stat_type.lower() == "exit":
            print("Exiting. Have a great day!")
            break
        elif stat_type.lower() == "striking":
            striking_headings, striking_stats = fighter.get_striking()
            # Create a table to show the striking statistics
            striking_df = pd.DataFrame(striking_stats, columns=striking_headings)
            print(tabulate(striking_df, showindex=False, headers=striking_headings))
        elif stat_type.lower() == "clinch":
            clinch_headings, clinch_stats = fighter.get_clinch()
            # Create a table to show the clinch statistics
            clinch_df = pd.DataFrame(clinch_stats, columns=clinch_headings)
            print(tabulate(clinch_df, showindex=False, headers=clinch_headings))
        elif stat_type.lower() == "ground":
            ground_headings, ground_stats = fighter.get_ground()
            # Create a table to show the ground statistics
            ground_df = pd.DataFrame(ground_stats, columns=ground_headings)
            print(tabulate(ground_df, showindex=False, headers=ground_headings))

        elif stat_type.lower() == "glossary":
            while True:
                # Glossary of each heading
                glossary_type = input("Would you like a glossary for striking, clinch, or ground? ")
                if glossary_type.lower() == "striking":
                    print("""
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
                    """)
                    break
                elif glossary_type.lower() == "clinch":
                    print("""
                    Glossary:
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
                    """)
                    break
                elif glossary_type.lower() == "ground":
                    print("""
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
                    """)
                    break
                else:
                    print("Invalid glossary type. Please choose 'striking', 'clinch', or 'ground'.")
        else:
            print("Invalid input. Please choose 'striking', 'clinch', or 'ground'.")

if __name__ == "__main__":
    main()