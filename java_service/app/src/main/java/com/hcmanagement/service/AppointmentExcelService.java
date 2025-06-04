package com.hcmanagement.service;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.ss.util.CellRangeAddress;
import org.apache.poi.xssf.usermodel.*;
import org.springframework.stereotype.Service;
import org.apache.poi.xddf.usermodel.chart.*;

import java.io.ByteArrayOutputStream;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class AppointmentExcelService {
    
    public byte[] generateAppointmentsExcel(List<Map<String, Object>> appointments) throws Exception {
        Workbook workbook = new XSSFWorkbook();
        XSSFSheet sheet = (XSSFSheet) workbook.createSheet("Citas");

        Row header = sheet.createRow(0);
        header.createCell(0).setCellValue("Fecha");
        header.createCell(1).setCellValue("Hora");
        header.createCell(2).setCellValue("Estado");
        header.createCell(3).setCellValue("Motivo");
        header.createCell(4).setCellValue("Diagnóstico");
        header.createCell(5).setCellValue("Tratamiento");
        header.createCell(6).setCellValue("Notas posteriores");
        header.createCell(7).setCellValue("Paciente");
        header.createCell(8).setCellValue("DNI Paciente");
        header.createCell(9).setCellValue("Doctor");
        header.createCell(10).setCellValue("DNI Doctor");

        int rowIdx = 1;
        for (Map<String, Object> appt : appointments) {
            Row row = sheet.createRow(rowIdx++);
            row.createCell(0).setCellValue(appt.getOrDefault("date", "").toString());
            row.createCell(1).setCellValue(appt.getOrDefault("time", "").toString());
            row.createCell(2).setCellValue(appt.getOrDefault("status", "").toString());
            row.createCell(3).setCellValue(appt.getOrDefault("reason", "").toString());
            row.createCell(4).setCellValue(appt.getOrDefault("diagnosis", "").toString()); 
            row.createCell(5).setCellValue(appt.getOrDefault("treatment", "").toString()); 
            row.createCell(6).setCellValue(appt.getOrDefault("notes", "").toString()); 
            row.createCell(7).setCellValue(
                appt.getOrDefault("patient_first_name", "") + " " + appt.getOrDefault("patient_last_name", "")
            );
            row.createCell(8).setCellValue(appt.getOrDefault("patient_dni", "").toString());
            row.createCell(9).setCellValue(
                appt.getOrDefault("doctor_first_name", "") + " " + appt.getOrDefault("doctor_last_name", "")
            );
            row.createCell(10).setCellValue(appt.getOrDefault("doctor_dni", "").toString());
        }

        Map<String, Integer> statusCount = new HashMap<>();
        for (Map<String, Object> appt : appointments) {
            String status = appt.getOrDefault("status", "").toString();
            statusCount.put(status, statusCount.getOrDefault(status, 0) + 1);
        }

        int chartDataStartRow = appointments.size() + 2;
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
        
        // --- Creación del gráfico ---
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
        return bos.toByteArray();
    }

}
