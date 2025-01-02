"""
File: gen_adf_doc.py
Description: This script parses an ARM file from ADF and generates the HTML documentation for the artifacts.
Author: Sanjay Ganvkar
Email: sanjay.ganvkar@gmail.com
Date: 2025-02-01
Version: 1.0
License: MIT License

Dependencies:
    - pandas (pip install pandas)
    - Any other dependencies

Usage:
    python gen_adf_doc.py --arm_template_file_path "./ARMTemplateForFactory.json" --html_file_path "adf_doc.html"
"""

import argparse
import json
import pandas as pd
from collections import defaultdict, deque

def convert_to_nested_table_html(obj, suppress_type_expression=False):
    html = "<table class='nested-table'>"
    for key, value in obj.items():
        if suppress_type_expression and key == "type" and value == "Expression":
            continue
        if isinstance(value, dict):
            nested_table = convert_to_nested_table_html(value, suppress_type_expression)
            html += f"<tr><td>{key}</td><td>{nested_table}</td></tr>"
        else:
            html += f"<tr><td>{key}</td><td>{value}</td></tr>"
    html += "</table>"
    return html

def extract_dataset_name(name):
    import re
    match = re.search(r"/([^/]+)'\)]$", name)
    if match:
        return match.group(1)
    else:
        return name

def topological_sort(activities):
    # Create a graph and in-degree count
    graph = defaultdict(list)
    in_degree = {activity["name"]: 0 for activity in activities}

    # Build the graph and in-degree count
    for activity in activities:
        if "dependsOn" in activity:
            for dependency in activity["dependsOn"]:
                graph[dependency["activity"]].append(activity["name"])
                in_degree[activity["name"]] += 1

    # Find all nodes with no incoming edges
    queue = deque([activity for activity in in_degree if in_degree[activity] == 0])

    sorted_activities = []
    while queue:
        node = queue.popleft()
        sorted_activities.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return sorted_activities

def sort_activities_by_dependency(activities):
    activity_dict = {activity["name"]: activity for activity in activities}
    sorted_activity_names = topological_sort(activities)
    return [activity_dict[name] for name in sorted_activity_names]

def generate_activity_html(activities):
    # Sort activities by dependency
    sorted_activities = sort_activities_by_dependency(activities)
    
    html_content = ""
    for activity in sorted_activities:
        activity_name = activity.get("name")
        activity_type = activity.get("type")
        depends_on = activity.get("dependsOn")
        user_properties = activity.get("userProperties")
        type_properties = activity.get("typeProperties")

        html_content += f"""
        <details>
            <summary><span class='marker'></span>Activity: {activity_name}</summary>
            <table class='activity-table'>
                <tr>
                    <th>Attribute</th>
                    <th>Details</th>
                </tr>
                <tr>
                    <td>Type</td>
                    <td>{activity_type}</td>
                </tr>
        """

        if depends_on:
            html_content += "<tr><td>Depends On</td><td><ul>"
            for dependency in depends_on:
                dependency_activity = dependency.get("activity")
                dependency_conditions = ", ".join(dependency.get("dependencyConditions", []))
                html_content += f"<li>Activity: {dependency_activity} (Conditions: {dependency_conditions})</li>"
            html_content += "</ul></td></tr>"

        if user_properties:
            user_properties_details = pd.DataFrame(user_properties).to_html(index=False)
            html_content += f"<tr><td>User Properties</td><td>{user_properties_details}</td></tr>"

        if type_properties:
            type_properties_html = convert_to_nested_table_html(type_properties)
            html_content += f"<tr><td>Type Properties</td><td>{type_properties_html}</td></tr>"

        if activity_type in ["IfCondition", "ForEach", "Switch"]:
            if "ifTrueActivities" in type_properties:
                html_content += "<tr><td>If True Activities</td><td>"
                html_content += generate_activity_html(type_properties["ifTrueActivities"])
                html_content += "</td></tr>"
            if "ifFalseActivities" in type_properties:
                html_content += "<tr><td>If False Activities</td><td>"
                html_content += generate_activity_html(type_properties["ifFalseActivities"])
                html_content += "</td></tr>"
            if "activities" in type_properties:
                html_content += "<tr><td>Activities</td><td>"
                html_content += generate_activity_html(type_properties["activities"])
                html_content += "</td></tr>"
            if "cases" in type_properties:
                for case in type_properties["cases"]:
                    case_value = case.get("value")
                    html_content += f"<tr><td>Case: {case_value}</td><td>"
                    html_content += generate_activity_html(case.get("activities", []))
                    html_content += "</td></tr>"

        html_content += "</table></details>"

    return html_content

def print_datasets_html(data):
    resources = data.get("resources", [])

    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Data Factory Datasets, Linked Services, and Pipelines</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h2, h3, h4 { color: #333; }
        hr { margin-block-start: 0.83em; margin-block-end: 0.83em; margin-inline-start: 0px; margin-inline-end: 0px; }
        table { width: 95%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { padding: 8px; text-align: left; border: 1px solid #ccc; }
        th { background-color: #f9f9f9; }
        ul { list-style-type: none; padding: 0; }
        ul li { margin: 2px 0; }
        ul li a { text-decoration: none; color: #1a73e8; }
        ul li a:hover { text-decoration: underline; }
        .nested-table { width: 100%; border-collapse: collapse; }
        .nested-table th, .nested-table td { padding: 8px; border: 1px solid #ddd; }
        .activity-table { width: 100%; border-collapse: collapse; }
        .activity-table th, .activity-table td { padding: 8px; border: 1px solid #ddd; }
        pre { margin: 0; font-family: monospace; }
        details summary { display: flex; align-items: center; cursor: pointer; }
        .marker { width: 0; height: 0; border-top: 5px solid transparent; border-bottom: 5px solid transparent; border-left: 10px solid #007bff; margin-right: 10px; }
        .dataset-name { color: #d1a419; }
        .linked-service-name { color: #33c3ff; }
        .pipeline-name { color: #2c0b4f; }
        .toc-table td { vertical-align: top; padding-right: 20px; }
    </style>
</head>
<body>
    <h2>MDM Hub ADF Artifacts</h2>
    <h3>Table of Contents</h3>
    <hr>
    <table class='toc-table'>
        <tr>
"""

    grouped_resources = {}
    for resource in resources:
        resource_type = resource["type"].split('/')[-1]
        if resource_type not in grouped_resources:
            grouped_resources[resource_type] = []
        grouped_resources[resource_type].append(resource)

    column_count = 0
    for group_name, group_resources in grouped_resources.items():
        capitalized_field = group_name.capitalize()
        if column_count % 3 == 0:
            html += "</tr><tr>"
        html += f"<td><h4>{capitalized_field}</h4><ul>"
        for resource in group_resources:
            name = extract_dataset_name(resource["name"])
            html += f"<li><a href='#{name}'>{name}</a></li>"
        html += "</ul></td>"
        column_count += 1

    html += "</tr></table><hr><h2>Artifact Details</h2><hr>"

    html += "<h3>Datasets</h3><table>"

    for resource in resources:
        if resource["type"] == "Microsoft.DataFactory/factories/datasets":
            name = extract_dataset_name(resource["name"])
            properties = resource["properties"]
            linked_service_name = properties["linkedServiceName"]["referenceName"]

            parameters_html = convert_to_nested_table_html(properties.get("parameters", {}))
            type_properties_html = convert_to_nested_table_html(properties.get("typeProperties", {}), suppress_type_expression=True)

            html += f"""
        <tr id='{name}'>
            <th colspan='2'><details><summary class='dataset-name'>{name}</summary>
            <table>
            <tr>
                <td>Linked Service Name</td>
                <td>{linked_service_name}</td>
            </tr>
            <tr>
                <td>Parameters</td>
                <td>{parameters_html}</td>
            </tr>
            <tr>
                <td>Type Properties</td>
                <td>{type_properties_html}</td>
            </table></details></th>
        </tr>
        """

    html += "</table>"

    html += "<h3>Linked Services</h3><table>"

    for resource in resources:
        if resource["type"] == "Microsoft.DataFactory/factories/linkedServices":
            name = extract_dataset_name(resource["name"])
            properties = resource["properties"]
            type_ = properties["type"]

            type_properties_html = convert_to_nested_table_html(properties.get("typeProperties", {}))

            html += f"""
        <tr id='{name}'>
            <th colspan='2'><details><summary class='linked-service-name'>{name}</summary>
            <table>
            <tr>
                <td>Type</td>
                <td>{type_}</td>
            </tr>
            <tr>
                <td>Type Properties</td>
                <td>{type_properties_html}</td>
            </table></details></th>
        </tr>
"""

    html += "</table>"

    html += "<h3>Pipelines</h3><table>"

    for resource in resources:
        if resource["type"] == "Microsoft.DataFactory/factories/pipelines":
            name = extract_dataset_name(resource["name"])
            properties = resource["properties"]
            parameters = properties.get("parameters", {})
            pipeline_description = properties.get("description")

            activities_html = generate_activity_html(properties.get("activities", []))

            html += f"""
                <tr id='{name}'>
                    <th colspan='2' class='pipeline-name'>{name}</th>
                  
                </tr>
                <tr>
                  <td colspan='2' class='xpipeline-name'>{pipeline_description}</td>
                </tr>
                
                <tr>
                    <td>Parameter Name</td>
                    <td>Type</td>
                </tr>
            """
            for parameter_name, parameter_value in parameters.items():
                parameter_type = parameter_value.get("type")
                html += f"""
                    <tr>
                        <td>{parameter_name}</td>
                        <td>{parameter_type}</td>
                    </tr>
                """

            html += f"""
        <tr>
            <td>Activities</td>
            <td>{activities_html}</td>
        </tr>
"""

    html += "</table></body></html>"

    return html

def main(arm_template_file_path, html_file_path):
    # Read the JSON file
    with open(arm_template_file_path, 'r') as f:
        data = json.load(f)

    html_content = print_datasets_html(data)

    # Write the HTML content to the output file
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML file created at {html_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate HTML documentation for ADF artifacts from an ARM template.")
    parser.add_argument("--arm_template_file_path", required=True, help="Path to the JSON file containing the ARM template.")
    parser.add_argument("--html_file_path", required=True, help="Path to the output HTML file.")

    args = parser.parse_args()

    main(args.arm_template_file_path, args.html_file_path)