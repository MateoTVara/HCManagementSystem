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
public class PatientExcelService {
    private final Cache<Integer, byte[]> reportCache = CacheBuilder.newBuilder()
        .maximumSize(100)
        .expireAfterWrite(10, TimeUnit.MINUTES)
        .build();

    public byte[] generatePatientsExcel(List<Map<String, Object>> patients) throws Exception {
        int cacheKey = patients.hashCode();
        byte[] cached = reportCache.getIfPresent(cacheKey);
        if (cached != null) return cached;

        Workbook workbook = new XSSFWorkbook();
        XSSFSheet sheet = (XSSFSheet)workbook.createSheet("Pacientes");

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
            "DNI", "Nombre", "Apellido", "Fecha de nacimiento", "Género",
            "Tipo de sangre", "Teléfono", "Dirección", "Correo electrónico"
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

        CellStyle allergyStyle = workbook.createCellStyle();
        allergyStyle.cloneStyleFrom(cellStyle);
        allergyStyle.setFillForegroundColor(IndexedColors.LIGHT_YELLOW.getIndex());
        allergyStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);

        CellStyle contactStyle = workbook.createCellStyle();
        contactStyle.cloneStyleFrom(cellStyle);
        contactStyle.setFillForegroundColor(IndexedColors.LIGHT_GREEN.getIndex());
        contactStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);

        int rowIdx = 1;
        for (Map<String, Object> patient : patients) {
            int mainRowIdx = rowIdx;
            Row row = sheet.createRow(rowIdx++);
            row.createCell(0).setCellValue(patient.getOrDefault("dni", "").toString());
            row.createCell(1).setCellValue(patient.getOrDefault("first_name", "").toString());
            row.createCell(2).setCellValue(patient.getOrDefault("last_name", "").toString());
            row.createCell(3).setCellValue(patient.getOrDefault("date_of_birth", "").toString());
            row.createCell(4).setCellValue(patient.getOrDefault("gender", "").toString());
            row.createCell(5).setCellValue(patient.getOrDefault("blood_type", "").toString());
            row.createCell(6).setCellValue(patient.getOrDefault("phone", "").toString());
            row.createCell(7).setCellValue(patient.getOrDefault("address", "").toString());
            row.createCell(8).setCellValue(patient.getOrDefault("email", "").toString());
            for (int i = 0; i < headers.length; i++) {
                row.getCell(i).setCellStyle(cellStyle);
            }

            // Subfilas: Alergias
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> allergies = (List<Map<String, Object>>) patient.get("allergies");
            if (allergies != null && !allergies.isEmpty()) {
                Row allergyHeader = sheet.createRow(rowIdx++);
                allergyHeader.createCell(1).setCellValue("Alergias (Nombre, Severidad, Reacciones)");
                for (int i = 0; i < headers.length; i++) {
                    Cell c = allergyHeader.getCell(i);
                    if (c == null) c = allergyHeader.createCell(i);
                    c.setCellStyle(subheaderStyle);
                }
                for (Map<String, Object> allergy : allergies) {
                    Row allergyRow = sheet.createRow(rowIdx++);
                    allergyRow.createCell(1).setCellValue("Nombre: " + allergy.getOrDefault("name", ""));
                    allergyRow.createCell(2).setCellValue("Severidad: " + allergy.getOrDefault("severity", ""));
                    allergyRow.createCell(3).setCellValue("Reacciones: " + allergy.getOrDefault("patient_reactions", ""));
                    for (int i = 0; i < headers.length; i++) {
                        Cell c = allergyRow.getCell(i);
                        if (c == null) c = allergyRow.createCell(i);
                        c.setCellStyle(allergyStyle);
                    }
                }
            }

            // Subfilas: Contactos de emergencia
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> contacts = (List<Map<String, Object>>) patient.get("emergency_contacts");
            if (contacts != null && !contacts.isEmpty()) {
                Row contactHeader = sheet.createRow(rowIdx++);
                contactHeader.createCell(1).setCellValue("Contactos de Emergencia (Nombre, Parentesco, Teléfono, Dirección)");
                for (int i = 0; i < headers.length; i++) {
                    Cell c = contactHeader.getCell(i);
                    if (c == null) c = contactHeader.createCell(i);
                    c.setCellStyle(subheaderStyle);
                }
                for (Map<String, Object> contact : contacts) {
                    Row contactRow = sheet.createRow(rowIdx++);
                    contactRow.createCell(1).setCellValue("Nombre: " + contact.getOrDefault("full_name", ""));
                    contactRow.createCell(2).setCellValue("Parentesco: " + contact.getOrDefault("relationship", ""));
                    contactRow.createCell(3).setCellValue("Teléfono: " + contact.getOrDefault("phone", ""));
                    contactRow.createCell(4).setCellValue("Dirección: " + contact.getOrDefault("address", ""));
                    for (int i = 0; i < headers.length; i++) {
                        Cell c = contactRow.getCell(i);
                        if (c == null) c = contactRow.createCell(i);
                        c.setCellStyle(contactStyle);
                    }
                }
            }

            // Subfilas: Historiales médicos
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> records = (List<Map<String, Object>>) patient.get("medical_records");
            if (records != null && !records.isEmpty()) {
                Row recHeader = sheet.createRow(rowIdx++);
                recHeader.createCell(1).setCellValue("Historiales Médicos (Fecha, Estado, Doctor, Notas)");
                for (int i = 0; i < headers.length; i++) {
                    Cell c = recHeader.getCell(i);
                    if (c == null) c = recHeader.createCell(i);
                    c.setCellStyle(subheaderStyle);
                }
                for (Map<String, Object> rec : records) {
                    Row recRow = sheet.createRow(rowIdx++);
                    recRow.createCell(1).setCellValue("Fecha: " + rec.getOrDefault("created_at", ""));
                    recRow.createCell(2).setCellValue("Estado: " + rec.getOrDefault("status", ""));
                    recRow.createCell(3).setCellValue("Doctor: " + rec.getOrDefault("attending_doctor", ""));
                    recRow.createCell(4).setCellValue("Notas: " + rec.getOrDefault("additional_notes", ""));
                    for (int i = 0; i < headers.length; i++) {
                        Cell c = recRow.getCell(i);
                        if (c == null) c = recRow.createCell(i);
                        c.setCellStyle(contactStyle);
                    }
                }
            }

            // Agrupa las filas detalle bajo la fila del paciente
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
