from create_data import CreateDataFields

# pd = glob.glob('charger_server/src/data/pd/*.csv')
# ppv = glob.glob('charger_server/src/data/ppv/*.csv')
data = CreateDataFields()
data.create_charger_file_data_only(1)
