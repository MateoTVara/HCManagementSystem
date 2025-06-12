package com.hcmanagement.service;

// Google Guava para el cache
import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;

// Apache POI para manipulación de archivos Excel
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.ss.util.CellRangeAddress;
import org.apache.poi.xssf.usermodel.*;
import org.apache.poi.xddf.usermodel.chart.*;

import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Service
public class AppointmentExcelService {
    // Cache para almacenar los reportes generados y evitar recalcularlos frecuentemente
    private final Cache<Integer, byte[]> reportCache = CacheBuilder.newBuilder()
        .maximumSize(100) // Máximo 100 reportes en cache
        .expireAfterWrite(10, TimeUnit.MINUTES) // Expiran después de 10 minutos
        .build();

    // Genera un archivo Excel con la información de las citas y un gráfico de estados
    public byte[] generateAppointmentsExcel(List<Map<String, Object>> appointments) throws Exception {
        int cacheKey = appointments.hashCode(); // Llave única para el cache basada en los datos
        byte[] cached = reportCache.getIfPresent(cacheKey); // Busca en cache
        if (cached != null) return cached; // Si existe, retorna el archivo cacheado

        // Crea la fila de encabezados con estilo
        Workbook workbook = new XSSFWorkbook();
        XSSFSheet sheet = (XSSFSheet) workbook.createSheet("Citas");

        // Estilo para la cabecera
        CellStyle headerStyle = workbook.createCellStyle();
        headerStyle.setFillForegroundColor(IndexedColors.LIGHT_CORNFLOWER_BLUE.getIndex());
        headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        headerStyle.setBorderBottom(BorderStyle.THIN);
        headerStyle.setBorderTop(BorderStyle.THIN);
        headerStyle.setBorderLeft(BorderStyle.THIN);
        headerStyle.setBorderRight(BorderStyle.THIN);
        Font font = workbook.createFont();
        font.setBold(true);
        headerStyle.setFont(font);

        // Crea la fila de encabezados
        Row header = sheet.createRow(0);
        String[] headers = {
            "Fecha", "Hora", "Estado", "Motivo", "Tratamiento", "Notas posteriores",
            "Paciente", "DNI Paciente", "Doctor", "DNI Doctor"
        };
        for (int i = 0; i < headers.length; i++) {
            Cell cell = header.createCell(i);
            cell.setCellValue(headers[i]);
            cell.setCellStyle(headerStyle);
        }

        // Estilo para las celdas normales con borde
        CellStyle cellStyle = workbook.createCellStyle();
        cellStyle.setBorderBottom(BorderStyle.THIN);
        cellStyle.setBorderTop(BorderStyle.THIN);
        cellStyle.setBorderLeft(BorderStyle.THIN);
        cellStyle.setBorderRight(BorderStyle.THIN);

        int rowIdx = 1;
        // Llena la hoja con los datos de las citas
        for (Map<String, Object> appt : appointments) {
            Row row = sheet.createRow(rowIdx++);
            row.createCell(0).setCellValue(appt.getOrDefault("date", "").toString());
            row.createCell(1).setCellValue(appt.getOrDefault("time", "").toString());
            row.createCell(2).setCellValue(appt.getOrDefault("status", "").toString());
            row.createCell(3).setCellValue(appt.getOrDefault("reason", "").toString());
            row.createCell(4).setCellValue(appt.getOrDefault("treatment", "").toString());
            row.createCell(5).setCellValue(appt.getOrDefault("notes", "").toString());
            row.createCell(6).setCellValue(
                appt.getOrDefault("patient_first_name", "") + " " + appt.getOrDefault("patient_last_name", "")
            );
            row.createCell(7).setCellValue(appt.getOrDefault("patient_dni", "").toString());
            row.createCell(8).setCellValue(
                appt.getOrDefault("doctor_first_name", "") + " " + appt.getOrDefault("doctor_last_name", "")
            );
            row.createCell(9).setCellValue(appt.getOrDefault("doctor_dni", "").toString());
            // Aplica el estilo a cada celda de la fila
            for (int i = 0; i < headers.length; i++) {
                row.getCell(i).setCellStyle(cellStyle);
            }
        }

        // Ajusta el ancho de las columnas automáticamente
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }

        // Cuenta la cantidad de citas por estado
        Map<String, Integer> statusCount = new HashMap<>();
        for (Map<String, Object> appt : appointments) {
            String status = appt.getOrDefault("status", "").toString();
            statusCount.put(status, statusCount.getOrDefault(status, 0) + 1);
        }

        // Escribe los datos del gráfico (estado y cantidad) en la hoja
        int chartDataStartRow = appointments.size() + 2;
        int i = 0;
        for (Map.Entry<String, Integer> entry : statusCount.entrySet()) {
            Row row = sheet.createRow(chartDataStartRow + i);
            row.createCell(0).setCellValue(entry.getKey());
            row.createCell(1).setCellValue(entry.getValue());
            i++;
        }

        // Define la posición y tamaño del gráfico en la hoja
        int chartColStart = 12;
        int chartColEnd = 20;
        int chartRowStart = 1;
        int chartRowEnd = 20;
        
        // --- Creación del gráfico ---
        XSSFDrawing drawing = sheet.createDrawingPatriarch(); // Crea el contenedor de gráficos
        XSSFClientAnchor anchor = drawing.createAnchor(
            0, 0, 0, 0,
            chartColStart, chartRowStart,
            chartColEnd, chartRowEnd
        );
        XSSFChart chart = drawing.createChart(anchor); // Crea el gráfico
        chart.setTitleText("Citas por Estado"); // Título del gráfico
        chart.setTitleOverlay(false);

        XDDFChartLegend legend = chart.getOrAddLegend(); // Agrega leyenda
        legend.setPosition(LegendPosition.TOP_RIGHT);

        XDDFCategoryAxis bottomAxis = chart.createCategoryAxis(AxisPosition.BOTTOM); // Eje X
        bottomAxis.setTitle("Estado");
        XDDFValueAxis leftAxis = chart.createValueAxis(AxisPosition.LEFT); // Eje Y
        leftAxis.setTitle("Cantidad");

        // Define los datos de categorías (estados) y valores (cantidades) para el gráfico
        XDDFDataSource<String> estados = XDDFDataSourcesFactory.fromStringCellRange(
            sheet,
            new CellRangeAddress(chartDataStartRow, chartDataStartRow + statusCount.size() - 1, 0, 0)
        );
        XDDFNumericalDataSource<Double> cantidades = XDDFDataSourcesFactory.fromNumericCellRange(
            sheet,
            new CellRangeAddress(chartDataStartRow, chartDataStartRow + statusCount.size() - 1, 1, 1)
        );

        // Crea el conjunto de datos y lo agrega al gráfico
        XDDFChartData data = chart.createData(ChartTypes.BAR, bottomAxis, leftAxis);
        XDDFChartData.Series series = data.addSeries(estados, cantidades);
        series.setTitle("Cantidad de Citas", null);
        chart.plot(data);

        // Escribe el libro Excel en un arreglo de bytes
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        workbook.write(bos);
        workbook.close();
        byte[] excelBytes = bos.toByteArray();
        reportCache.put(cacheKey, excelBytes); // Guarda el resultado en cache
        return excelBytes; // Retorna el archivo Excel generado
    }

}
