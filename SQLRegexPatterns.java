import javax.swing.*;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SQLRegexPatterns {
    public static void main(String[] args) {
        String[] bas = {
                "create database .*;",
                "drop database .*;",
                "use .*;",
                "close .*;",
                "create table .* (.*\\);",
                "drop table .*;",
                "select table .*;",
                "insert into .* \\(.*\\) values \\(.*\\);",
                "update .* set .*=.* where .*[>,<,=].*;",
                "select .* from .* where .*[<,>,=].*;",
                "delete from .* where .*[<,>,=].*;"
        };

        // Test SQL queries against the regular expressions
        String testSQL = "create database TestDB;";
        checkSQLSyntax(bas, testSQL);
    }
    public static void createTable(String sql, JTextArea outputTextArea) {
    // 检查数据库连接
    String pattern = "select\\s+(.*?)\\s+from\\s+(\\w+)\\s+where\\s+(.*?);";
    Pattern r = Pattern.compile(pattern);
    Matcher m = r.matcher(sql);
    String error=null;
        if (!isOpen) {
        error="未连接数据库";
        outputTextArea.append(error+"\n");
        System.out.println(error);
        return;
    }

    String dataRange = null;
    String tableName = null;
    String condition = null;

        if (m.find()) {
        dataRange = m.group(1);
        tableName = m.group(2);
        condition = m.group(3);
    } else {
        error="无法解析 SQL 语句";
        outputTextArea.append(error+"\n");
        System.out.println(error);
        return;
    }

    File dataFile = new File(prePath + File.separator + tableName + ".data");

        if (!dataFile.exists()) {
        error="数据文件不存在";
        System.out.println("数据文件不存在");
        outputTextArea.append(error+"\n");
        return;
    }

    List<String> getL = Arrays.asList(dataRange.split(","));
    String[] conditionSplit = condition.split("[><=]");

        if (conditionSplit.length != 2) {
        error="条件格式错误";
        System.out.println("条件格式错误");
        outputTextArea.append(error+"\n");
        return;
    }

    String gl = conditionSplit[0].trim();
    String inf = conditionSplit[1].trim();

    // 重新匹配正确的表
    int pos = -1;
        for (int i = 0; i < tables.size(); ++i) {
        if (tables.get(i).getName().equals(tableName)) {
            pos = i;
            break;
        }
    }

        if (pos == -1) {
        error="表名不存在";
        System.out.println("表名不存在");
        outputTextArea.append(error+"\n");
        return;
    }
    //获得需要的range数据
    List<Integer> checkLine = new ArrayList<>();
        for (int i = 0; i < tables.get(pos).getLines().size(); ++i) {
        if (getL.contains(tables.get(pos).getLines().get(i).getName())) {
            checkLine.add(i);
        }
    }

    List<String> showData = new ArrayList<>();
        try (
    BufferedReader reader = new BufferedReader(new FileReader(dataFile))) {
        String line;
        while ((line = reader.readLine()) != null) {
            String[] columns = line.split("\t");
            StringBuilder tmp = new StringBuilder();
            boolean isShow = false;
            List<String> con = new ArrayList<>();
            for (int j = 0; j < tables.get(pos).getLines().size(); ++j) {
                String tmpStr = columns[j];
                boolean b=tables.get(pos).getLines().get(j).getName().equals(gl);
                if (b &&tmpStr.equals(inf)) {
                    isShow = true;
                }
                for (int k : checkLine) {
                    if (j == k) {
                        con.add(tmpStr);
                        break;
                    }
                }
            }
            if (isShow) {
                tmp.append(String.join("\t", con));
                showData.add(tmp.toString());
            }
        }
    } catch (
    IOException e) {
        e.printStackTrace();
    }
    StringBuilder columnsOutput = new StringBuilder();
        for (String column : getL) {
        columnsOutput.append(column).append("\t");
    }
        columnsOutput.append("\n"); // 添加换行
        outputTextArea.append(columnsOutput.toString()); // 将列名输出到文本区域

    // 输出数据到文本区域
        for (String data : showData) {
        outputTextArea.append(data+"\n"); // 输出数据到文本区域，并在每条数据后添加换行
    }
    // 输出列名
        for (String column : getL) {
        System.out.print(column + "\t");
    }
        System.out.println();

    // 输出数据
        for (String data : showData) {
        System.out.println(data);
    }
    public static void checkSQLSyntax(String[] patterns, String query) {
        for (String pattern : patterns) {
            if (Pattern.matches(pattern, query)) {
                return;
            }
        }
        System.out.println("语法错误" + query);
    }
}
