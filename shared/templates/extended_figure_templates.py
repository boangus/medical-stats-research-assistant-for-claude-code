
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

PALETTE = {
    'blue_main': '#0F4D92',
    'blue_secondary': '#3775BA',
    'green_1': '#DDF3DE',
    'green_2': '#AADCA9',
    'green_3': '#8BCF8B',
    'red_1': '#F6CFCB',
    'red_2': '#E9A6A1',
    'red_strong': '#B64342',
    'neutral_light': '#CFCECE',
    'neutral_mid': '#767676',
    'neutral_dark': '#4D4D4D',
    'gold': '#FFD700',
    'teal': '#42949E',
    'violet': '#9A4D8E',
}

COLOR_BLIND_SAFE = [
    '#0072B2', '#E69F00', '#009E73', '#F0E442',
    '#56B4E9', '#D55E00', '#CC79A7',
]


def format_p_value(p: float, precision: int = 3) -> str:
    if p < 0.001:
        return 'P < 0.001'
    elif p < 1.0:
        return f'P = {p:.{precision}f}'
    else:
        return 'P = 1.000'


def make_histogram(data, bins='auto', xlabel=None, ylabel='Frequency',
                   title=None, color=None, figsize=(6, 4)):
    if color is None:
        color = PALETTE['blue_main']
    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(data, bins=bins, color=color, edgecolor='white', alpha=0.8)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_density_plot(data, xlabel=None, ylabel='Density',
                      title=None, color=None, figsize=(6, 4)):
    if color is None:
        color = PALETTE['blue_main']
    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(data, bins='auto', density=True, color=color,
            alpha=0.3, edgecolor='none')
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(data)
    xvals = np.linspace(min(data), max(data), 200)
    ax.plot(xvals, kde(xvals), color=color, linewidth=2.0)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_violin_plot(data, labels, xlabel=None, ylabel=None,
                     title=None, colors=None, figsize=(7, 4)):
    if colors is None:
        colors = COLOR_BLIND_SAFE[:len(data)]
    fig, ax = plt.subplots(figsize=figsize)
    parts = ax.violinplot(data, showmeans=False, showmedians=True,
                          showextrema=True)
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i % len(colors)])
        pc.set_alpha(0.7)
    for key in ['cbars', 'cmaxes', 'cmines', 'cmedians']:
        parts[key].set_color('black')
        parts[key].set_linewidth(1.0)
    ax.set_xticks(np.arange(1, len(labels) + 1))
    ax.set_xticklabels(labels, fontsize=9)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_dot_plot(data, labels, xlabel=None, ylabel=None,
                  title=None, colors=None, figsize=(7, 4)):
    if colors is None:
        colors = COLOR_BLIND_SAFE[:len(data)]
    fig, ax = plt.subplots(figsize=figsize)
    for i, (d, color) in enumerate(zip(data, colors)):
        x = np.random.normal(i + 1, 0.04, size=len(d))
        ax.scatter(x, d, s=30, color=color, alpha=0.8,
                   edgecolors='white', linewidth=0.5)
    ax.set_xticks(np.arange(1, len(labels) + 1))
    ax.set_xticklabels(labels, fontsize=9)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_pie_chart(values, labels, title=None, colors=None,
                   autopct='%1.1f%%', figsize=(5, 5)):
    if colors is None:
        colors = COLOR_BLIND_SAFE[:len(values)]
    fig, ax = plt.subplots(figsize=figsize)
    wedges, texts, autotexts = ax.pie(values, labels=labels,
                                       colors=colors, autopct=autopct,
                                       startangle=90, textprops={'fontsize': 9})
    ax.axis('equal')
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    fig.tight_layout(pad=2)
    return fig, ax


def make_line_graph(x, y, xlabel=None, ylabel=None, title=None,
                    color=None, show_ci=True, ci_lower=None,
                    ci_upper=None, figsize=(7, 4)):
    if color is None:
        color = PALETTE['blue_main']
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(x, y, color=color, linewidth=2.0, marker='o', markersize=6)
    if show_ci and ci_lower is not None and ci_upper is not None:
        ax.fill_between(x, ci_lower, ci_upper, color=color, alpha=0.15)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_area_chart(x, y, xlabel=None, ylabel=None, title=None,
                    color=None, figsize=(7, 4)):
    if color is None:
        color = PALETTE['blue_main']
    fig, ax = plt.subplots(figsize=figsize)
    ax.fill_between(x, y, color=color, alpha=0.3)
    ax.plot(x, y, color=color, linewidth=2.0)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_bubble_plot(x, y, size, xlabel=None, ylabel=None, title=None,
                     color=None, figsize=(6, 5)):
    if color is None:
        color = PALETTE['blue_main']
    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(x, y, s=size, color=color, alpha=0.6,
               edgecolors='white', linewidth=0.5)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_pair_plot(data, columns=None, title=None, figsize=(8, 8)):
    if columns is None:
        columns = list(data.columns)
    n = len(columns)
    fig, axes = plt.subplots(n, n, figsize=figsize)
    for i in range(n):
        for j in range(n):
            ax = axes[i, j]
            if i == j:
                ax.hist(data[columns[i]], bins='auto',
                        color=PALETTE['blue_main'], alpha=0.6)
            else:
                ax.scatter(data[columns[j]], data[columns[i]],
                           s=20, color=PALETTE['blue_main'],
                           alpha=0.5, edgecolors='none')
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            if j == 0:
                ax.set_ylabel(columns[i], fontsize=8)
            else:
                ax.set_ylabel('')
                ax.set_yticklabels([])
            if i == n - 1:
                ax.set_xlabel(columns[j], fontsize=8)
            else:
                ax.set_xlabel('')
                ax.set_xticklabels([])
    if title:
        fig.suptitle(title, fontsize=12, fontweight='bold', y=0.98)
    fig.tight_layout(pad=1)
    return fig, axes


def make_bland_altman_plot(x1, x2, xlabel=None, ylabel='Difference',
                           title=None, color=None, figsize=(6, 5)):
    if color is None:
        color = PALETTE['blue_main']
    x1 = np.asarray(x1)
    x2 = np.asarray(x2)
    mean_vals = (x1 + x2) / 2
    diff = x1 - x2
    mean_diff = np.mean(diff)
    std_diff = np.std(diff)
    upper_limit = mean_diff + 1.96 * std_diff
    lower_limit = mean_diff - 1.96 * std_diff
    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(mean_vals, diff, s=40, color=color, alpha=0.7,
               edgecolors='white', linewidth=0.5)
    ax.axhline(mean_diff, color='black', linestyle='-', linewidth=1.5)
    ax.axhline(upper_limit, color=PALETTE['red_strong'],
               linestyle='--', linewidth=1.0)
    ax.axhline(lower_limit, color=PALETTE['red_strong'],
               linestyle='--', linewidth=1.0)
    from scipy import stats
    r, p_val = stats.pearsonr(mean_vals, diff)
    ax.text(0.05, 0.95,
            f'Mean diff = {mean_diff:.3f}\n95% LOA: {lower_limit:.3f} to {upper_limit:.3f}\nr = {r:.3f} ({format_p_value(p_val)})',
            transform=ax.transAxes, fontsize=8, va='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor='none', alpha=0.8))
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    else:
        ax.set_xlabel('Mean of two measurements', fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_decision_curve(prob_thresholds, net_benefit,
                        treat_all=None, treat_none=None,
                        xlabel='Threshold Probability',
                        ylabel='Net Benefit', title=None,
                        color=None, figsize=(7, 5)):
    if color is None:
        color = PALETTE['blue_main']
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(prob_thresholds, net_benefit, color=color,
            linewidth=2.0, label='Model')
    if treat_all is not None:
        ax.plot(prob_thresholds, treat_all, color=PALETTE['neutral_mid'],
                linestyle='--', linewidth=1.0, label='Treat all')
    if treat_none is not None:
        ax.plot(prob_thresholds, treat_none, color=PALETTE['neutral_light'],
                linestyle=':', linewidth=1.0, label='Treat none')
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_xlim(0, 1)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_funnel_plot(effect_sizes, standard_errors,
                     xlabel='Effect Size', ylabel='Standard Error',
                     title=None, color=None, figsize=(5, 5)):
    if color is None:
        color = PALETTE['blue_main']
    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(effect_sizes, standard_errors, s=60, color=color,
               edgecolors='black', linewidth=0.5)
    ax.axvline(np.mean(effect_sizes), color=PALETTE['neutral_mid'],
               linestyle='--', linewidth=1.0, alpha=0.8)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.invert_yaxis()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_rmst_plot(time, event, group, group_labels=None,
                   group_colors=None, xlabel='Time',
                   ylabel='RMST', title=None, figsize=(7, 5)):
    from lifelines import KaplanMeierFitter
    time = np.asarray(time)
    event = np.asarray(event)
    group = np.asarray(group)
    groups = np.unique(group)
    if group_labels is None:
        group_labels = [str(g) for g in groups]
    if group_colors is None:
        group_colors = COLOR_BLIND_SAFE[:len(groups)]
    fig, ax = plt.subplots(figsize=figsize)
    for i, (g, label, color) in enumerate(zip(groups, group_labels, group_colors)):
        mask = group == g
        kmf = KaplanMeierFitter()
        kmf.fit(time[mask], event[mask], label=label)
        rmst = kmf.restricted_mean_survival_time_
        ax.plot(kmf.timeline, kmf.cumulative_density_,
                color=color, linewidth=2.0)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_consort_flowchart(total_assessed, excluded_screening, randomized,
                           allocated_intervention, allocated_control,
                           excluded_post_randomization, analyzed_intervention,
                           analyzed_control, title='CONSORT Flow Diagram',
                           figsize=(8, 10)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    from matplotlib.patches import FancyBboxPatch
    y = 95
    box_height = 6
    box_width = 28

    def add_box(text, x, y, color='white'):
        box = FancyBboxPatch((x, y), box_width, box_height,
                             boxstyle='round,pad=0.3',
                             facecolor=color, edgecolor='black', linewidth=1.0)
        ax.add_patch(box)
        ax.text(x + box_width/2, y + box_height/2, text,
                ha='center', va='center', fontsize=10)
        return y - box_height - 2

    def add_arrow(x1, y1, x2, y2, direction='down'):
        if direction == 'down':
            ax.annotate('', xy=(x1, y2), xytext=(x2, y1),
                        arrowprops=dict(arrowstyle='->', linewidth=1.0))

    y = add_box(f'Patients assessed for eligibility
(n = {total_assessed})', 25, y)
    add_arrow(39, y + 8, 39, y + 2)
    y = add_box(f'Excluded
(n = {excluded_screening})', 25, y)
    add_arrow(39, y + 8, 39, y + 2)
    y = add_box(f'Randomized
(n = {randomized})', 25, y)
    add_arrow(39, y + 8, 39, y + 2)
    y_intervention = y - 8
    y_control = y - 8
    add_box(f'Allocated to intervention
(n = {allocated_intervention})', 10, y_intervention)
    add_box(f'Allocated to control
(n = {allocated_control})', 50, y_control)
    y_intervention -= 10
    y_control -= 10
    if excluded_post_randomization > 0:
        add_box(f'Excluded post-randomization
(n = {excluded_post_randomization})', 10, y_intervention)
        add_box(f'Excluded post-randomization
(n = {excluded_post_randomization})', 50, y_control)
        y_intervention -= 10
        y_control -= 10
    add_box(f'Analyzed
(n = {analyzed_intervention})', 10, y_intervention)
    add_box(f'Analyzed
(n = {analyzed_control})', 50, y_control)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 80)
    ax.set_ylim(0, 100)
    return fig, ax


def make_cumulative_incidence_curve(time, event, competing_event,
                                     group=None, group_labels=None,
                                     xlabel='Time', ylabel='Cumulative Incidence',
                                     title=None, colors=None, figsize=(7, 5)):
    from lifelines import CumulativeIncidenceFitter
    time = np.asarray(time)
    event = np.asarray(event)
    competing_event = np.asarray(competing_event)
    if colors is None:
        colors = COLOR_BLIND_SAFE
    fig, ax = plt.subplots(figsize=figsize)
    if group is not None:
        group = np.asarray(group)
        groups = np.unique(group)
        if group_labels is None:
            group_labels = [str(g) for g in groups]
        for i, (g, label, color) in enumerate(zip(groups, group_labels, colors)):
            mask = group == g
            cif = CumulativeIncidenceFitter()
            cif.fit(time[mask], event[mask], competing_event[mask], label=label)
            cif.plot(ax=ax, color=color)
    else:
        cif = CumulativeIncidenceFitter()
        cif.fit(time, event, competing_event)
        cif.plot(ax=ax, color=colors[0])
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


def make_det_curve(y_true, y_score, xlabel='False Positive Rate',
                   ylabel='Detection Rate', title=None,
                   color=None, figsize=(5, 5)):
    from sklearn.metrics import det_curve
    fpr, fnr, thresholds = det_curve(y_true, y_score)
    if color is None:
        color = PALETTE['blue_main']
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(fpr, fnr, color=color, linewidth=2.0)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.tight_layout(pad=2)
    return fig, ax


__all__ = [
    'make_histogram', 'make_density_plot', 'make_violin_plot',
    'make_dot_plot', 'make_pie_chart', 'make_line_graph',
    'make_area_chart', 'make_bubble_plot', 'make_pair_plot',
    'make_bland_altman_plot', 'make_decision_curve',
    'make_funnel_plot', 'make_rmst_plot', 'make_consort_flowchart',
    'make_cumulative_incidence_curve', 'make_det_curve',
]
