tables = ["AnsweredQs", "CRQuestions", "DSQuestions", "PSQuestions", "SCQuestions"]
for t in tables:
	print("""CREATE TRIGGER {0}_ondelete AFTER DELETE ON {0}
BEGIN
    INSERT INTO modifications (table_name, action) VALUES ('{0}','DELETE');
END;
CREATE TRIGGER {0}_oninsert AFTER INSERT ON {0}
BEGIN
    INSERT INTO modifications (table_name, action) VALUES ('{0}','INSERT');
END;
CREATE TRIGGER {0}_onupdate AFTER UPDATE ON {0}
BEGIN
    INSERT INTO modifications (table_name, action) VALUES ('{0}','UPDATE');
END;""".format(t))