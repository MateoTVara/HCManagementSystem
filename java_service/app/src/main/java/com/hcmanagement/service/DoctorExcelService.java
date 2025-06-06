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

        Row header = sheet.createRow(0);
        header.createCell(0).setCellValue("DNI");
        header.createCell(1).setCellValue("Nombre");
        header.createCell(2).setCellValue("Apellido");
        header.createCell(3).setCellValue("Correo electrónico");
        header.createCell(4).setCellValue("Especialidad");
        header.createCell(5).setCellValue("Género");

        int rowIdx = 1;
        for (Map<String, Object> doctor : doctors) {
            Row row = sheet.createRow(rowIdx++);
            row.createCell(0).setCellValue(doctor.getOrDefault("dni", "").toString());
            row.createCell(1).setCellValue(doctor.getOrDefault("first_name", "").toString());
            row.createCell(2).setCellValue(doctor.getOrDefault("last_name", "").toString());
            row.createCell(3).setCellValue(doctor.getOrDefault("email", "").toString());
            row.createCell(4).setCellValue(doctor.getOrDefault("specialty", "").toString());
            row.createCell(5).setCellValue(doctor.getOrDefault("gender", "").toString());
        }

        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        workbook.write(bos);
        workbook.close();
        byte[] excelBytes = bos.toByteArray();
        reportCache.put(cacheKey, excelBytes);
        return excelBytes;
    }

}
