Python script will generate html documentation from your Azure Data Factory ARM template

To Use

1. Clone the Repository or download the gen_adf_doc.py

2. Set Up Python Environment
You’ll need Python 3.7+ and this package:

 pip install pandas

3. Export ARM Template from ADF
In ADF Studio:

Go to Manage > ARM template > Export ARM Template

Extract the ARMTemplateForFactory.json from the dowloaded Template zip file and copy to the folder where you have the gen_adf_doc.py

4. Run the Script

python gen_adf_doc.py --arm_template_file_path "./ARMTemplateForFactory.json" --html_file_path "adf_doc.html"
 
Try and self document the artifacts and pipelines using the Descriptions  ( Available in the Properties/etc) in the ADF itself,
thereby making your documentation self-contained and upto-date. Subsequently , you just have to run the script to
generate the HTML documentation as a quick reference

Have fun.

Sanjay Ganvkar

**Mocked up html output**


![adf](https://github.com/user-attachments/assets/d594782e-6c08-408d-9de5-2770c90e02fe)


