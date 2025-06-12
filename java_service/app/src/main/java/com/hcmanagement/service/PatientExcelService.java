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

        int rowIdx = 1;
        for (Map<String, Object> patient : patients) {
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
