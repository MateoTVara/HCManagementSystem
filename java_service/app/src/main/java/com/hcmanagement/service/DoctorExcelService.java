package com.hcmanagement.service;

import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.*;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Service
public class DoctorExcelService {
    private final Cache<Integer, byte[]> reportCache = CacheBuilder.newBuilder()
        .maximumSize(100)
        .expireAfterWrite(10, TimeUnit.MINUTES)
        .build();

    public byte[] generateDoctorsExcel(List<Map<String, Object>> doctors) throws Exception {
        int cacheKey = doctors.hashCode();
        byte[] cached = reportCache.getIfPresent(cacheKey);
        if (cached != null) return cached;

        Workbook workbook = new XSSFWorkbook();
        XSSFSheet sheet = (XSSFSheet) workbook.createSheet("Doctores");

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
        String[] headers = {
            "DNI", "Nombre", "Apellido", "Correo electrónico", "Especialidad", "Género"
        };
        Row header = sheet.createRow(0);
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

        // Subheader y detalle estilos
        CellStyle subheaderStyle = workbook.createCellStyle();
        subheaderStyle.cloneStyleFrom(cellStyle);
        subheaderStyle.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.getIndex());
        subheaderStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        Font subFont = workbook.createFont();
        subFont.setBold(true);
        subheaderStyle.setFont(subFont);

        CellStyle appointmentStyle = workbook.createCellStyle();
        appointmentStyle.cloneStyleFrom(cellStyle);
        appointmentStyle.setFillForegroundColor(IndexedColors.LIGHT_YELLOW.getIndex());
        appointmentStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);

        int rowIdx = 1;
        for (Map<String, Object> doctor : doctors) {
            int mainRowIdx = rowIdx;
            Row row = sheet.createRow(rowIdx++);
            row.createCell(0).setCellValue(doctor.getOrDefault("dni", "").toString());
            row.createCell(1).setCellValue(doctor.getOrDefault("first_name", "").toString());
            row.createCell(2).setCellValue(doctor.getOrDefault("last_name", "").toString());
            row.createCell(3).setCellValue(doctor.getOrDefault("email", "").toString());
            row.createCell(4).setCellValue(doctor.getOrDefault("specialty", "").toString());
            row.createCell(5).setCellValue(doctor.getOrDefault("gender", "").toString());
            for (int i = 0; i < headers.length; i++) {
                row.getCell(i).setCellStyle(cellStyle);
            }

            // Subfilas: Citas asociadas
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> appointments = (List<Map<String, Object>>) doctor.get("appointments");
            if (appointments != null && !appointments.isEmpty()) {
                Row apptHeader = sheet.createRow(rowIdx++);
                apptHeader.createCell(1).setCellValue("Citas (Fecha, Hora, Estado, Paciente, DNI, Motivo)");
                for (int i = 0; i < headers.length; i++) {
                    Cell c = apptHeader.getCell(i);
                    if (c == null) c = apptHeader.createCell(i);
                    c.setCellStyle(subheaderStyle);
                }
                for (Map<String, Object> appt : appointments) {
                    Row apptRow = sheet.createRow(rowIdx++);
                    apptRow.createCell(1).setCellValue("Fecha: " + appt.getOrDefault("date", ""));
                    apptRow.createCell(2).setCellValue("Hora: " + appt.getOrDefault("time", ""));
                    apptRow.createCell(3).setCellValue("Estado: " + appt.getOrDefault("status", ""));
                    apptRow.createCell(4).setCellValue("Paciente: " + appt.getOrDefault("patient_name", ""));
                    apptRow.createCell(5).setCellValue("DNI: " + appt.getOrDefault("patient_dni", ""));
                    apptRow.createCell(6).setCellValue("Motivo: " + appt.getOrDefault("reason", ""));
                    for (int i = 0; i < headers.length; i++) {
                        Cell c = apptRow.getCell(i);
                        if (c == null) c = apptRow.createCell(i);
                        c.setCellStyle(appointmentStyle);
                    }
                }
            }

            // Subfilas: Historiales médicos asociados
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> records = (List<Map<String, Object>>) doctor.get("medical_records");
            if (records != null && !records.isEmpty()) {
                Row recHeader = sheet.createRow(rowIdx++);
                recHeader.createCell(1).setCellValue("Historiales Médicos (Fecha, Estado, Paciente, DNI, Notas)");
                for (int i = 0; i < headers.length; i++) {
                    Cell c = recHeader.getCell(i);
                    if (c == null) c = recHeader.createCell(i);
                    c.setCellStyle(subheaderStyle);
                }
                for (Map<String, Object> rec : records) {
                    Row recRow = sheet.createRow(rowIdx++);
                    recRow.createCell(1).setCellValue("Fecha: " + rec.getOrDefault("created_at", ""));
                    recRow.createCell(2).setCellValue("Estado: " + rec.getOrDefault("status", ""));
                    recRow.createCell(3).setCellValue("Paciente: " + rec.getOrDefault("patient_name", ""));
                    recRow.createCell(4).setCellValue("DNI: " + rec.getOrDefault("patient_dni", ""));
                    recRow.createCell(5).setCellValue("Notas: " + rec.getOrDefault("additional_notes", ""));
                    for (int i = 0; i < headers.length; i++) {
                        Cell c = recRow.getCell(i);
                        if (c == null) c = recRow.createCell(i);
                        c.setCellStyle(appointmentStyle);
                    }
                }
            }

            // Agrupa las filas detalle bajo la fila del doctor
            if (rowIdx - 1 > mainRowIdx) {
                sheet.groupRow(mainRowIdx + 1, rowIdx - 1);
                sheet.setRowGroupCollapsed(mainRowIdx + 1, true);
            }
        }

        // Ajusta el ancho de las columnas automáticamente
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }

        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        workbook.write(bos);
        workbook.close();
        byte[] excelBytes = bos.toByteArray();
        reportCache.put(cacheKey, excelBytes);
        return excelBytes;
    }
}
