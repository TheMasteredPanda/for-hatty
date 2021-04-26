import asyncio
from matplotlib import pyplot as plt
from ukparliament import ukparliament
from ukparliament.structures.members import ElectionResult
import random
import string


def generate_election_graphic(parliament, result: ElectionResult,
                              include_nonvoters: bool = False,
                              generate_table: bool = False):
    under_1k = []
    the_rest = []
    candidates = result.get_candidates()

    for candidate in candidates:
        if candidate['votes'] > 1000:
            the_rest.append(candidate)
        else: 
            under_1k.append(candidate)

    nonvoters = result.get_electorate_size() - result.get_turnout()
    under_1k_total = sum([c['votes'] for c in under_1k])
    parent_pie_values = [c['votes'] for c in the_rest]
    parent_pie_labels = [f"{(parliament.get_party_by_id(c['party_id']).get_abber() if parliament.get_party_by_id(c['party_id']) is not None else c['party_name']) if c['party_name'] != 'UK Independence Party' else 'UKIP'}" + f" ({c['votes']:,} votes)" for c in the_rest]
    if under_1k_total != 0: 
        parent_pie_values.append(under_1k_total)
        parent_pie_labels.append(f'Others ({under_1k_total:,} votes)')
    if nonvoters != 0 and include_nonvoters: 
        parent_pie_values.append(nonvoters)
        parent_pie_labels.append(f"Didn't Vote ({nonvoters:,} votes)")

    # make figure and assign axis objects
    plt.tight_layout()
    fig, ax1 = plt.subplots()

    # large pie chart parameters
    # explode = [0.1, 0, 0]
    # rotate so that first wedge is split by the x-axis

    if generate_table is False:
        ax1.pie(parent_pie_values, radius=0.6,
                labels=parent_pie_labels)
    else:
        ax1.set_axis_off()
        table = ax1.table(cellText=[[c['name'], c['party_name'] if c['party_name'] != 'UK Independence Party' else 'UKIP', f"{c['votes']:,}",
                          "{:.1%}".format(c['vote_share']), c['vote_share_change']] for c in result.get_candidates()], loc='upper center', 
                          colLabels=['Candidate', 'Party', 'Votes', 'Vote Share', 'Vote Share Change'], cellLoc='center')

        table.auto_set_column_width(col=list(range(len(result.get_candidates()))))
        cells = table.get_celld()

        for i in range(5):
            for j in range(0, 13):
                cells[(j, i)].set_height(.065)

        table.auto_set_font_size(False)

    file_id = ''.join(random.choice(string.ascii_letters) for i in range(15))
    plt.savefig(f'{file_id}.png')


parliament = ukparliament.UKParliament()
asyncio.run(parliament.load())
member = parliament.get_commons_members()[0]
elections = asyncio.run(parliament.get_election_results(member))
generate_election_graphic(parliament, elections[0])
