function setup_data_table(table_def, table_id, toggle_columns_id) {
    table_def.forEach(function(entry, idx) {
        if (!('name' in entry)) { // do not overwrite existing name value (select)
            entry['name'] = entry['data']; // use same data field for editor and table
        }
        entry['targets'] = [idx];

        // add data columns to table
        $(table_id).find('tr').append('<th>' + entry['label'] + '</th>')
    });
}
