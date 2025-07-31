import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive Agg
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

def create_graphs(money_data, demographic_data):
    """Generate property value and demographic charts based on input data.
    
    Args:
        money_data: List of dictionaries containing yearly financial data (with $ and commas)
        demographic_data: Dictionary containing racial demographic percentages
    """
    # Create images directory if it doesn't exist
    os.makedirs('images', exist_ok=True)
    
    # Create property value assessment history chart
    _create_money_graph(money_data)
    
    # Create demographic pie chart
    _create_demographic_graph(demographic_data)

def _convert_money_string(money_str):
    """Convert money string like '$11,623' to float 11623.0"""
    if isinstance(money_str, (int, float)):
        return float(money_str)
    return float(money_str.replace('$', '').replace(',', ''))

def _create_money_graph(money_data):
    # Extract and clean data from input
    years = [entry['year'] for entry in money_data]
    assessment_values = [_convert_money_string(entry['tax_assessment_total']) for entry in money_data]
    
    # Create figure with custom styling
    plt.figure(figsize=(10, 6))

    # Set custom fonts
    plt.rcParams['font.family'] = 'Open Sans'
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.labelsize'] = 14

    # Plot the data with custom styling
    ax = plt.subplot()
    line = ax.plot(years, assessment_values, 
                   marker='o', 
                   markersize=8,
                   linewidth=3,
                   color='#004272',
                   markerfacecolor='#2a7f62',
                   markeredgewidth=1.5,
                   markeredgecolor='white')

    # Formatting
    ax.set_title('Property Value Assessment History', 
                 pad=20, 
                 fontname='Merriweather',
                 color='#004272')
    ax.set_xlabel('Year', labelpad=10)
    ax.set_ylabel('Assessment Value ($)', labelpad=10)

    # Custom grid and spines
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e0e0e0')
    ax.spines['bottom'].set_color('#e0e0e0')

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))

    # Custom ticks
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_xticks(years)
    plt.xticks(rotation=45, ha='right')

    # Add value annotations
    for x, y in zip(years, assessment_values):
        ax.annotate(f'${y/1000:.0f}k', 
                    (x, y),
                    textcoords="offset points",
                    xytext=(0,10),
                    ha='center',
                    fontsize=10,
                    color='#555555')

    # Add subtle background
    ax.set_facecolor('none')

    # Add growth percentage annotation if there's enough data
    if len(assessment_values) > 1:
        growth_pct = (assessment_values[0] - assessment_values[-1]) / assessment_values[-1] * 100
        ax.text(0.02, 0.95, 
                f'+{growth_pct:.1f}% growth since {years[-1]}', 
                transform=ax.transAxes,
                fontsize=12,
                bbox=dict(facecolor='white', edgecolor='#e0e0e0', boxstyle='round,pad=0.5'))

    plt.tight_layout()
    plt.savefig('images/money_graph.png', dpi=300, bbox_inches='tight', transparent=True)
    plt.close()

def _create_demographic_graph(demographic_data):
    # Filter out any groups with 0% to avoid clutter
    filtered_demo = {k: v for k, v in demographic_data.items() if v > 0}
    
    # Original color palette (extended for possible additional groups)
    colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948', '#b07aa1']
    explode = (0,) * len(filtered_demo)  # No explosion

    # Create figure with original styling
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot pie chart (shadow=False)
    wedges, texts, autotexts = ax.pie(
        filtered_demo.values(),
        explode=explode,
        colors=colors[:len(filtered_demo)],
        labels=filtered_demo.keys(),
        autopct='%1.1f%%',
        startangle=90,
        shadow=False,
        textprops={'fontsize': 13, 'fontweight': 'bold'},
        wedgeprops={'linewidth': 1, 'edgecolor': 'white', 'alpha': 0.9},
        pctdistance=0.85
    )

    # Percentage text styling
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)

    ax.axis('equal')  # Perfect circle

    # Title
    plt.title(
        'Community Racial Distribution',
        fontsize=18,
        fontweight='bold',
        pad=20,
        color='#333333'
    )

    # Legend
    legend = ax.legend(
        wedges,
        [f"{k} ({v}%)" for k, v in filtered_demo.items()],
        title="Ethnic Groups",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        prop={'size': 12}
    )
    legend.get_title().set_fontweight('bold')

    # White edges
    for wedge in wedges:
        wedge.set_edgecolor('#f5f5f5')
        wedge.set_linewidth(0.5)

    # Context note
    plt.text(
        0.5, -0.1,
        'Data represents percentage of population by racial group',
        ha='center',
        transform=ax.transAxes,
        fontsize=10,
        color='#666666'
    )

    # Backgrounds
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('none')

    plt.tight_layout()
    plt.savefig('images/demographic_graph.png', dpi=300, bbox_inches='tight', transparent=True)
    plt.close()
