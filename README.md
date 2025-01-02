Python script will generate html documentation from your Azure Data Factory ARM template

To Use

Export the ARM template of your ADF

Run the python script as below ( you will requre pandas )

python gen_adf_doc.py --arm_template_file_path "./ARMTemplateForFactory.json" --html_file_path "adf_doc.html"

Try and self document the artifacts and pipelines using the Descriptions  ( Available in the Properties/etc) in the ADF itself,
thereby making your documentation self-contained and upto-date. Subsequently , you just have to run the script to
generate the HTML documentation as a quick reference

Have fun.

Sanjay Ganvkar

