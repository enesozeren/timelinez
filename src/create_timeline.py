import argparse
import json
import plotly.graph_objects as go
from datetime import datetime
import os

def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def process_data(data):
    # Convert date strings to datetime objects and sort by date
    for entry in data:
        entry['date'] = datetime.strptime(entry['date'], '%Y-%m-%d')
    data.sort(key=lambda x: x['date'])
    return data

def split_text(text, length_threshold):
    words = text.split()
    new_text = ""
    line_length = 0

    for word in words:
        if line_length + len(word) + 1 > length_threshold:
            new_text += "<br>"
            line_length = 0
        elif new_text:
            new_text += " "
        
        new_text += word
        line_length += len(word) + 1
    
    return new_text

def create_timeline(data, output_file, length_threshold=30):
    dates = [entry['date'] for entry in data]
    event_names = [split_text(entry['event_name'], length_threshold) for entry in data]
    authors = [", ".join(entry['authors']) for entry in data]
    summaries = [entry['summary'] for entry in data]

    fig = go.Figure()

    # Alternate events between top and bottom
    for i, (date, event_name, author, summary) in enumerate(zip(dates, event_names, authors, summaries)):
        y_position = 1 if i % 2 == 0 else -1
        hover_text = f"<b>Date:</b> {date.strftime('%Y-%m-%d')}<br><b>{event_name}</b><br><br><b>Authors:</b> {author}<br><b>Summary:</b> {summary}"
        
        fig.add_trace(go.Scatter(
            x=[date],
            y=[y_position],
            text=event_name,
            hovertext=hover_text,
            mode="markers+text",
            textposition="top center" if y_position == 1 else "bottom center",
            hoverinfo="text",
            marker=dict(color="blue", size=10),
        ))

    # Add a central line
    fig.add_shape(
        type="line",
        x0=min(dates),
        y0=0,
        x1=max(dates),
        y1=0,
        line=dict(color="black", width=2),
    )

    # Formatting
    fig.update_layout(
        title="Interactive AI History Timeline",
        showlegend=False,
        xaxis=dict(
            title="Date",
            showgrid=True,
            zeroline=False,
            tickformat="%Y-%m-%d",
        ),
        yaxis=dict(
            visible=False,
            range=[-2, 2],
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        height=600,
    )

    # Save the plot as an HTML file
    fig.write_html(output_file)
    print(f"Timeline saved as {output_file}")

def main(json_file_path, output_dir):
    if not os.path.exists(json_file_path):
        print(f"File {json_file_path} does not exist.")
        return

    data = load_json(json_file_path)
    processed_data = process_data(data)
    create_timeline(processed_data, output_dir)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--json_file_path', type=str, required=True)
    argparser.add_argument('--output_file_name', type=str, default='timeline.html')
    args = argparser.parse_args()
    
    output_dir = os.path.join('timelines', args.output_file_name)
    os.makedirs('timelines', exist_ok=True)
    main(args.json_file_path, output_dir)