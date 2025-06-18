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
    private final Cache<Integer, byte[]> reportCache = CacheBuilder.newBuilder()
        .maximumSize(100)
        .expireAfterWrite(10, TimeUnit.MINUTES)
        .build();

    public byte[] generateAppointmentsExcel(List<Map<String, Object>> appointments) throws Exception {
        int cacheKey = appointments.hashCode();
        byte[] cached = reportCache.getIfPresent(cacheKey);
        if (cached != null) return cached;

        Workbook workbook = new XSSFWorkbook();
        XSSFSheet sheet = (XSSFSheet) workbook.createSheet("Citas");

        // Estilos
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

        CellStyle cellStyle = workbook.createCellStyle();
        cellStyle.setBorderBottom(BorderStyle.THIN);
        cellStyle.setBorderTop(BorderStyle.THIN);
        cellStyle.setBorderLeft(BorderStyle.THIN);
        cellStyle.setBorderRight(BorderStyle.THIN);

        // Estilo para subheader
        CellStyle subheaderStyle = workbook.createCellStyle();
        subheaderStyle.cloneStyleFrom(cellStyle);
        subheaderStyle.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.getIndex());
        subheaderStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        Font subFont = workbook.createFont();
        subFont.setBold(true);
        subheaderStyle.setFont(subFont);

        // Estilos para detalles
        CellStyle diagnosisStyle = workbook.createCellStyle();
        diagnosisStyle.cloneStyleFrom(cellStyle);
        diagnosisStyle.setFillForegroundColor(IndexedColors.LIGHT_YELLOW.getIndex());
        diagnosisStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);

        CellStyle prescriptionStyle = workbook.createCellStyle();
        prescriptionStyle.cloneStyleFrom(cellStyle);
        prescriptionStyle.setFillForegroundColor(IndexedColors.LIGHT_GREEN.getIndex());
        prescriptionStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);

        CellStyle examStyle = workbook.createCellStyle();
        examStyle.cloneStyleFrom(cellStyle);
        examStyle.setFillForegroundColor(IndexedColors.LIGHT_CORNFLOWER_BLUE.getIndex()); // Distinto a prescripción
        examStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);

        // Encabezados
        String[] headers = {
            "Fecha", "Hora", "Estado", "Motivo", "Tratamiento", "Notas posteriores",
            "Paciente", "DNI Paciente", "Doctor", "DNI Doctor"
        };
        Row header = sheet.createRow(0);
        for (int i = 0; i < headers.length; i++) {
            Cell cell = header.createCell(i);
            cell.setCellValue(headers[i]);
            cell.setCellStyle(headerStyle);
        }

        int rowIdx = 1;
        for (Map<String, Object> appt : appointments) {
            int mainRowIdx = rowIdx;
            // Fila principal de la cita
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
            for (int i = 0; i < headers.length; i++) {
                row.getCell(i).setCellStyle(cellStyle);
            }

            // Diagnósticos asociados
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> diagnoses = (List<Map<String, Object>>) appt.get("diagnoses");
            if (diagnoses != null && !diagnoses.isEmpty()) {
                Row diagHeader = sheet.createRow(rowIdx++);
                diagHeader.createCell(1).setCellValue("Diagnósticos (Código, Nombre, Notas)");
                for (int i = 0; i < headers.length; i++) {
                    Cell c = diagHeader.getCell(i);
                    if (c == null) c = diagHeader.createCell(i);
                    c.setCellStyle(subheaderStyle);
                }
                for (Map<String, Object> diag : diagnoses) {
                    Row diagRow = sheet.createRow(rowIdx++);
                    diagRow.createCell(1).setCellValue("Código: " + diag.getOrDefault("code_4", ""));
                    diagRow.createCell(2).setCellValue("Nombre: " + diag.getOrDefault("name", ""));
                    diagRow.createCell(3).setCellValue("Notas: " + diag.getOrDefault("notes", ""));
                    for (int i = 0; i < headers.length; i++) {
                        Cell c = diagRow.getCell(i);
                        if (c == null) c = diagRow.createCell(i);
                        c.setCellStyle(diagnosisStyle);
                    }
                }
            }

            // Prescripciones asociadas
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> prescriptions = (List<Map<String, Object>>) appt.get("prescriptions");
            if (prescriptions != null && !prescriptions.isEmpty()) {
                Row prescHeader = sheet.createRow(rowIdx++);
                prescHeader.createCell(1).setCellValue("Prescripciones (Medicamento, Dosis, Instrucciones)");
                for (int i = 0; i < headers.length; i++) {
                    Cell c = prescHeader.getCell(i);
                    if (c == null) c = prescHeader.createCell(i);
                    c.setCellStyle(subheaderStyle);
                }
                for (Map<String, Object> presc : prescriptions) {
                    Row prescRow = sheet.createRow(rowIdx++);
                    prescRow.createCell(1).setCellValue("Medicamento: " + presc.getOrDefault("medication", ""));
                    prescRow.createCell(2).setCellValue("Dosis: " + presc.getOrDefault("dosage", ""));
                    prescRow.createCell(3).setCellValue("Instrucciones: " + presc.getOrDefault("instructions", ""));
                    for (int i = 0; i < headers.length; i++) {
                        Cell c = prescRow.getCell(i);
                        if (c == null) c = prescRow.createCell(i);
                        c.setCellStyle(prescriptionStyle);
                    }
                }
            }

            // Exámenes asociados
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> exams = (List<Map<String, Object>>) appt.get("exams");
            if (exams != null && !exams.isEmpty()) {
                Row examHeader = sheet.createRow(rowIdx++);
                examHeader.createCell(1).setCellValue("Exámenes (Tipo de Examen)");
                for (int i = 0; i < headers.length; i++) {
                    Cell c = examHeader.getCell(i);
                    if (c == null) c = examHeader.createCell(i);
                    c.setCellStyle(subheaderStyle);
                }
                for (Map<String, Object> exam : exams) {
                    Row examRow = sheet.createRow(rowIdx++);
                    examRow.createCell(1).setCellValue("Tipo: " + exam.getOrDefault("exam_type", ""));
                    for (int i = 0; i < headers.length; i++) {
                        Cell c = examRow.getCell(i);
                        if (c == null) c = examRow.createCell(i);
                        c.setCellStyle(examStyle);
                    }
                }
            }

            // Agrupa las filas detalle bajo la fila de la cita
            if (rowIdx - 1 > mainRowIdx) {
                sheet.groupRow(mainRowIdx + 1, rowIdx - 1);
                sheet.setRowGroupCollapsed(mainRowIdx + 1, true);
            }
        }

        // Ajusta el ancho de las columnas automáticamente
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }

        // --- Gráfico de estados (igual que antes) ---
        Map<String, Integer> statusCount = new HashMap<>();
        for (Map<String, Object> appt : appointments) {
            String status = appt.getOrDefault("status", "").toString();
            statusCount.put(status, statusCount.getOrDefault(status, 0) + 1);
        }
        int chartDataStartRow = rowIdx + 2;
        int i = 0;
        for (Map.Entry<String, Integer> entry : statusCount.entrySet()) {
            Row row = sheet.createRow(chartDataStartRow + i);
            row.createCell(0).setCellValue(entry.getKey());
            row.createCell(1).setCellValue(entry.getValue());
            i++;
        }
        int chartColStart = 12;
        int chartColEnd = 20;
        int chartRowStart = 1;
        int chartRowEnd = 20;

        XSSFDrawing drawing = sheet.createDrawingPatriarch();
        XSSFClientAnchor anchor = drawing.createAnchor(
            0, 0, 0, 0,
            chartColStart, chartRowStart,
            chartColEnd, chartRowEnd
        );
        XSSFChart chart = drawing.createChart(anchor);
        chart.setTitleText("Citas por Estado");
        chart.setTitleOverlay(false);

        XDDFChartLegend legend = chart.getOrAddLegend();
        legend.setPosition(LegendPosition.TOP_RIGHT);

        XDDFCategoryAxis bottomAxis = chart.createCategoryAxis(AxisPosition.BOTTOM);
        bottomAxis.setTitle("Estado");
        XDDFValueAxis leftAxis = chart.createValueAxis(AxisPosition.LEFT);
        leftAxis.setTitle("Cantidad");

        XDDFDataSource<String> estados = XDDFDataSourcesFactory.fromStringCellRange(
            sheet,
            new CellRangeAddress(chartDataStartRow, chartDataStartRow + statusCount.size() - 1, 0, 0)
        );
        XDDFNumericalDataSource<Double> cantidades = XDDFDataSourcesFactory.fromNumericCellRange(
            sheet,
            new CellRangeAddress(chartDataStartRow, chartDataStartRow + statusCount.size() - 1, 1, 1)
        );

        XDDFChartData data = chart.createData(ChartTypes.BAR, bottomAxis, leftAxis);
        XDDFChartData.Series series = data.addSeries(estados, cantidades);
        series.setTitle("Cantidad de Citas", null);
        chart.plot(data);

        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        workbook.write(bos);
        workbook.close();
        byte[] excelBytes = bos.toByteArray();
        reportCache.put(cacheKey, excelBytes);
        return excelBytes;
    }
}
