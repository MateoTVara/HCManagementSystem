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

        int rowIdx = 1;
        for (Map<String, Object> doctor : doctors) {
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
