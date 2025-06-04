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

        Row header = sheet.createRow(0);
        header.createCell(0).setCellValue("DNI");
        header.createCell(1).setCellValue("Nombre");
        header.createCell(2).setCellValue("Apellido");
        header.createCell(3).setCellValue("Fecha de nacimiento");
        header.createCell(4).setCellValue("Género");
        header.createCell(5).setCellValue("Tipo de sangre");
        header.createCell(6).setCellValue("Teléfono");
        header.createCell(7).setCellValue("Dirección");
        header.createCell(8).setCellValue("Correo electrónico");

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
        }

        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        workbook.write(bos);
        workbook.close();

        byte[] excelBytes = bos.toByteArray();
        reportCache.put(cacheKey, excelBytes);
        return excelBytes;
    }
    
}
