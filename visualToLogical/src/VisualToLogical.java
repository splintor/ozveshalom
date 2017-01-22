import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.text.Bidi;
import java.util.regex.Pattern;

/**
 * Utility that uses {@link Bidi} class.
 * http://www.nesterovsky-bros.com/weblog/2013/07/28/VisualToLogicalConversionInJava.aspx
 */
public class VisualToLogical
{
    public static void main(String[] argv) {
        String root = argv[0];
        final File folder = new File(root);
        for (final File fileEntry : folder.listFiles()) {
            convertFileIiNeeded(root + File.separator + fileEntry.getName());
        }
    }

    private static void convertFileIiNeeded(String filename) {
        try {
            Reader in = new InputStreamReader(new FileInputStream(filename), "iso-8859-8");
            final StringBuilder out = new StringBuilder();
            final char[] buffer = new char[100000];
            for (; ; ) {
                int rsz = in.read(buffer, 0, buffer.length);
                if (rsz < 0)
                    break;
                out.append(buffer, 0, rsz);
            }
            String content = out.toString();
            if(!content.contains("charset=iso-8859-8")) {
                return; // no conversion needed
            }

            String converted = visualToLogical(content);
            converted = converted.replaceFirst("charset=iso-8859-8", "");
            converted = Pattern.compile("^>([A-Za-z\\<\\>0-9/]+)/<(.*)$", Pattern.MULTILINE).matcher(converted).replaceAll("$2</$1>");
            converted = Pattern.compile("^>([A-Za-z\\<\\>0-9/]+)<(.*)$", Pattern.MULTILINE).matcher(converted).replaceAll("$2<$1>");
            converted = Pattern.compile("^>(.*)<BR(.)(.*)$", Pattern.MULTILINE).matcher(converted).replaceAll("$3$2$1<BR>");
            converted = Pattern.compile("<([A-Za-z0-9]+)/>").matcher(converted).replaceAll("</$1>");
            converted = Pattern.compile(";([A-Za-z]+)&", Pattern.MULTILINE).matcher(converted).replaceAll("&$1;");
            //noinspection SpellCheckingInspection
            filename = filename.replaceFirst("\\.htm", "-converted.htm");
            Writer writer = new BufferedWriter(new OutputStreamWriter(  new FileOutputStream(filename), "iso-8859-8"));
            writer.write(converted);
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    /**
     * Implements visual to logical order converter.
     *
     * <a href="http://www.nesterovsky-bros.com">Nesterovsky bros</a>
     *
     * @param text an input text in visual order to convert.
     * @return a String value in logical order.
     */
    @SuppressWarnings("SpellCheckingInspection")
    private static String visualToLogical(String text)
    {
        if ((text == null) || (text.length() == 0))
        {
            return text;
        }

        Bidi bidi = new Bidi(text, Bidi.DIRECTION_DEFAULT_LEFT_TO_RIGHT);

        if (bidi.isLeftToRight())
        {
            return text;
        }

        int count = bidi.getRunCount();
        byte[] levels = new byte[count];
        Integer[] runs = new Integer[count];

        for (int i = 0; i < count; i++)
        {
            levels[i] = (byte)bidi.getRunLevel(i);
            runs[i] = i;
        }

        Bidi.reorderVisually(levels, 0, runs, 0, count);

        StringBuilder result = new StringBuilder();

        for (int i = 0; i < count; i++)
        {
            int index = runs[i];
            int start = bidi.getRunStart(index);
            int end = bidi.getRunLimit(index);
            int level = levels[index];

            if ((level & 1) != 0)
            {
                for (; --end >= start;)
                {
                    result.append(text.charAt(end));
                }
            }
            else
            {
                result.append(text, start, end);
            }
        }

        return result.toString();
    }
}